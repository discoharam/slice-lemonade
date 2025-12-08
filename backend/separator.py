import os,base64,subprocess,wave,audioop,json,shutil,tempfile
from datetime import datetime
from flask import current_app
from .runpod_client import RunPodClient
class AudioSeparator:
 def __init__(self):
  self.supported_formats=['.mp3','.wav','.flac','.m4a','.aac']
  self.format_mime_types={'mp3':'audio/mpeg','wav':'audio/wav','flac':'audio/flac'}
  self.runpod_client=RunPodClient()
 def get_audio_info(self,file_path:str)->dict:
  info={'channels':2,'sample_rate':44100,'duration':0,'bit_depth':16,'format':os.path.splitext(file_path)[1].lower().replace('.','')}
  try:
   cmd=['ffprobe','-v','error','-show_entries','stream=channels,sample_rate,duration:format=duration','-show_entries','format=bit_rate','-of','json',file_path]
   result=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
   if result.returncode==0:
    data=json.loads(result.stdout)
    if 'streams'in data and len(data['streams'])>0:
     stream=data['streams'][0]
     info['channels']=stream.get('channels',2)
     info['sample_rate']=stream.get('sample_rate',44100)
     info['duration']=float(stream.get('duration',0))
    if'format'in data:
     format_data=data['format']
     if'duration'in format_data:
      info['duration']=float(format_data['duration'])
     if'bit_rate'in format_data:
      info['bit_rate']=format_data['bit_rate']
  except Exception as e:print(f"⚠️ Audio info extraction failed:{e}")
  return info
 def convert_to_format(self,input_path,output_path,target_format,quality='high'):
  target_format=target_format.lower()
  if target_format=='mp3':
   quality_params={'high':['-codec:a','libmp3lame','-b:a','320k','-q:a','0','-joint_stereo','0'],'medium':['-codec:a','libmp3lame','-b:a','192k','-q:a','2'],'low':['-codec:a','libmp3lame','-b:a','128k','-q:a','4']}
  elif target_format=='flac':
   quality_params={'high':['-codec:a','flac','-compression_level','8'],'medium':['-codec:a','flac','-compression_level','5'],'low':['-codec:a','flac','-compression_level','2']}
  elif target_format=='wav':
   quality_params={'high':['-codec:a','pcm_s24le','-ar','48000'],'medium':['-codec:a','pcm_s16le','-ar','44100'],'low':['-codec:a','pcm_s16le','-ar','22050']}
  else:
   target_format='mp3'
   quality_params={'high':['-codec:a','libmp3lame','-b:a','320k','-q:a','0']}
  if quality not in quality_params:quality='high'
  cmd=['ffmpeg','-y','-i',input_path]+quality_params[quality]+[output_path]
  try:
   result=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
   if result.returncode!=0:raise Exception(f"FFmpeg conversion failed:{result.stderr[:200]}")
   return True
  except subprocess.TimeoutExpired:raise Exception("Conversion timeout")
  except Exception as e:raise Exception(f"Conversion error:{str(e)}")
 def trim_audio(self,input_path,output_path,start_time,end_time):
  duration=end_time-start_time
  if duration<0.1:raise Exception("Trim segment must be at least 0.1 seconds")
  cmd=['ffmpeg','-y','-i',input_path,'-ss',str(start_time),'-to',str(end_time),'-c:a','pcm_s16le','-ar','44100','-ac','2','-filter:a','loudnorm=I=-16:LRA=11:TP=-1.5','-fflags','+genpts',output_path]
  try:
   result=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
   if result.returncode!=0:raise Exception(f"Trim failed:{result.stderr[:200]}")
   if os.path.exists(output_path)and os.path.getsize(output_path)>1024:return True
   else:raise Exception("Trimmed file is empty or too small")
  except subprocess.TimeoutExpired:raise Exception("Trim operation timeout")
  except Exception as e:raise Exception(f"Trim error:{str(e)}")
 def separate_audio(self,input_path,job_id,output_format='mp3',quality='high',start_time=None,end_time=None):
  try:
   output_dir=os.path.normpath(os.path.join(current_app.config['RESULTS_FOLDER'],job_id))
   os.makedirs(output_dir,exist_ok=True)
   print(f"\n{'='*60}\n🎯 PROFESSIONAL AUDIO SEPARATION PROCESS\n{'='*60}")
   print(f"📂 Processing:{os.path.basename(input_path)}")
   print(f"📁 Job ID:{job_id}")
   print(f"📂 Output dir:{output_dir}")
   print(f"🎚️ Quality:{quality}(320kbps MP3)")
   audio_info=self.get_audio_info(input_path)
   is_input_mono=audio_info['channels']==1
   print(f"🎛️ Audio Info:{audio_info['channels']} channel{'s'if audio_info['channels']!=1 else''},{audio_info['sample_rate']}Hz,{audio_info['duration']:.2f}s")
   print(f"📡 Format:{audio_info['format'].upper()}")
   processing_path=input_path
   trim_info={}
   original_duration=audio_info['duration']
   if start_time is not None and end_time is not None:
    if start_time<0:start_time=0
    if end_time<=start_time:raise Exception("End time must be greater than start time")
    if end_time>original_duration:end_time=original_duration
    if end_time-start_time<0.1:raise Exception("Trim segment must be at least 0.1 seconds")
    print(f"\n✂️ TRIMMING AUDIO\n Original:{original_duration:.2f}s\n Selected:{start_time:.2f}s - {end_time:.2f}s\n Duration:{end_time-start_time:.2f}s")
    trimmed_path=os.path.join(output_dir,"trimmed_input.wav")
    try:
     if self.trim_audio(input_path,trimmed_path,start_time,end_time):
      processing_path=trimmed_path
      trim_info={'trimmed':True,'start_time':start_time,'end_time':end_time,'duration':end_time-start_time,'original_duration':original_duration,'savings_percent':round(((original_duration-(end_time-start_time))/original_duration)*100,1)}
      print(f"✅ Trim successful:{end_time-start_time:.2f}s segment")
      print(f"💰 Savings:{trim_info['savings_percent']}% less processing")
    except Exception as e:
     print(f"⚠️ Trim error, using original file:{str(e)}")
     trim_info={'trimmed':False,'error':str(e)}
   else:print("📋 Processing full audio file (no trim)");trim_info={'trimmed':False}
   file_size=os.path.getsize(processing_path)
   print(f"📊 Processing size:{file_size:,} bytes({file_size/1024/1024:.1f} MB)")
   print(f"\n🚀 SENDING TO RUNPOD GPU\n Endpoint:{self.runpod_client.endpoint_id}")
   result=self.runpod_client.separate_audio(processing_path,job_id,output_format,quality)
   print(f"\n🔍 RUNPOD RESPONSE ANALYSIS")
   if isinstance(result,dict)and'error'in result:
    error_msg=result['error']
    print(f"❌ RunPod returned error:{error_msg}")
    raise Exception(f"RunPod error:{error_msg}")
   stems=None
   if isinstance(result,dict):
    if'stems'in result:
     stems=result['stems']
     print(f"✅ Found stems in result.stems:{list(stems.keys())}")
    elif'output'in result and isinstance(result['output'],dict)and'stems'in result['output']:
     stems=result['output']['stems']
     print(f"✅ Found stems in result.output.stems:{list(stems.keys())}")
    else:
     for key in['vocals','drums','bass','other']:
      if key in result:
       if not stems:stems={}
       stems[key]=result[key]
     if stems:print(f"✅ Found stems directly in result:{list(stems.keys())}")
   if not stems:
    print(f"❌ No stems found in any format")
    if isinstance(result,dict):print(f" Result keys:{list(result.keys())}")
    else:print(f" Result type:{type(result)}")
    raise Exception("No stems generated")
   print(f"✅ Found{len(stems)} stems:{list(stems.keys())}")
   results_data={}
   saved_count=0
   total_original_size=0
   total_compressed_size=0
   for stem_name,stem_base64 in stems.items():
    try:
     if not stem_base64 or len(stem_base64)<100:
      print(f"⚠️ Stem{stem_name} has insufficient data({len(stem_base64)} chars)")
      continue
     stem_bytes=base64.b64decode(stem_base64)
     if len(stem_bytes)<1000:
      print(f"⚠️ Stem{stem_name} decoded to only{len(stem_bytes)} bytes")
      continue
     total_original_size+=len(stem_bytes)
     mp3_path=os.path.normpath(os.path.join(output_dir,f"{stem_name}.mp3"))
     with open(mp3_path,'wb')as f:f.write(stem_bytes)
     mp3_size=os.path.getsize(mp3_path)
     print(f"✅ Saved{stem_name}.mp3({mp3_size:,} bytes) - 320kbps")
     total_compressed_size+=mp3_size
     converted_formats=['mp3']
     wav_path=os.path.normpath(os.path.join(output_dir,f"{stem_name}.wav"))
     try:
      if self.convert_to_format(mp3_path,wav_path,'wav','high'):
       wav_size=os.path.getsize(wav_path)
       converted_formats.append('wav')
       print(f"✅ Created{stem_name}.wav({wav_size:,} bytes) - 24-bit professional")
     except Exception as e:print(f"⚠️ WAV conversion failed for{stem_name}:{str(e)}")
     flac_path=os.path.normpath(os.path.join(output_dir,f"{stem_name}.flac"))
     try:
      if self.convert_to_format(mp3_path,flac_path,'flac','high'):
       flac_size=os.path.getsize(flac_path)
       converted_formats.append('flac')
       print(f"✅ Created{stem_name}.flac({flac_size:,} bytes) - lossless professional")
     except Exception as e:print(f"⚠️ FLAC conversion failed for{stem_name}:{str(e)}")
     stem_is_mono=False
     try:
      temp_wav=os.path.join(output_dir,f"temp_{stem_name}.wav")
      cmd=['ffmpeg','-y','-i',mp3_path,'-acodec','pcm_s16le','-ar','44100',temp_wav]
      subprocess.run(cmd,capture_output=True,timeout=10)
      if os.path.exists(temp_wav):
       with wave.open(temp_wav,'rb')as wav:stem_is_mono=wav.getnchannels()==1
       os.remove(temp_wav)
     except:pass
     format_links={}
     for fmt in converted_formats:format_links[fmt]=f"/api/download/{job_id}/{stem_name}?format={fmt}"
     results_data[stem_name]={"formats":format_links,"primary":'mp3',"is_mono":stem_is_mono,"can_convert_to_mono":not stem_is_mono}
     saved_count+=1
    except Exception as e:
     print(f"⚠️ Error processing{stem_name}:{str(e)}")
     import traceback;traceback.print_exc()
   if saved_count==0:raise Exception("No stems could be saved")
   if processing_path!=input_path and os.path.exists(processing_path):
    try:os.remove(processing_path);print(f"🧹 Cleaned up trimmed temp file")
    except:pass
   compression_ratio=total_original_size/max(total_compressed_size,1)
   response={"job_id":job_id,"status":"completed","stems":results_data,"stems_count":saved_count,"primary_format":"mp3","quality":quality,"timestamp":datetime.utcnow().isoformat(),"trim_info":trim_info,"audio_info":{"original_channels":"mono"if is_input_mono else"stereo","original_duration":round(original_duration,2),"processing_stats":{"compression_ratio":round(compression_ratio,2),"original_size_mb":round(total_original_size/(1024*1024),2),"compressed_size_mb":round(total_compressed_size/(1024*1024),2),"savings_mb":round((total_original_size-total_compressed_size)/(1024*1024),2)}},"note":f"Professional audio separation completed - {saved_count} stems available in multiple formats"}
   if trim_info.get('trimmed'):
    response['savings_percent']=trim_info['savings_percent']
    response['original_duration']=trim_info['original_duration']
    response['trimmed_duration']=trim_info['duration']
    print(f"💰 Final savings:{trim_info['savings_percent']}% processing reduction")
   print(f"\n{'='*60}\n✅ SEPARATION COMPLETE - SUMMARY\n{'='*60}")
   print(f"📊 Stems generated: {saved_count}")
   print(f"📦 Compression ratio: {compression_ratio:.2f}x")
   print(f"💾 Size reduction: {((total_original_size - total_compressed_size) / (1024 * 1024)):.1f} MB")
   print(f"🎚️ Quality: {quality} (320kbps MP3)")
   if 'processing_time' in response:print(f"🕐 Processing time: {response.get('processing_time', 'N/A')}")
   if trim_info.get('trimmed'):print(f"✂️ Trim savings: {trim_info['savings_percent']}%")
   print('='*60)
   return response
  except Exception as e:
   print(f"\n{'='*60}\n❌ SEPARATION FAILED\n{'='*60}")
   print(f"Error:{str(e)}")
   import traceback;traceback.print_exc()
   if'processing_path'in locals()and processing_path!=input_path and os.path.exists(processing_path):
    try:os.remove(processing_path)
    except:pass
   try:
    output_dir=os.path.normpath(os.path.join(current_app.config['RESULTS_FOLDER'],job_id))
    if os.path.exists(output_dir):shutil.rmtree(output_dir,ignore_errors=True)
   except:pass
   return{"job_id":job_id,"status":"error","error":str(e),"timestamp":datetime.utcnow().isoformat()}