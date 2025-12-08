from flask import Blueprint,request,jsonify,send_file,current_app;import os,uuid;from werkzeug.utils import secure_filename;from .separator import AudioSeparator
main=Blueprint('main',__name__);separator=AudioSeparator()
def allowed_file(filename):
 allowed=separator.supported_formats
 return '.' in filename and filename.rsplit('.',1)[1].lower() in [ext[1:] for ext in allowed]
@main.route('/')
def home():return jsonify({"message":"Slice Lemonade API","status":"running","version":"3.1.0","features":["professional-quality","mp3-320kbps","wav-24bit","flac-lossless","gpu-accelerated","audio-trimming","smart-storage"]})
@main.route('/api/health',methods=['GET'])
def health_check():return jsonify({"status":"healthy","service":"slice-lemonade-pro","storage_initialized":current_app.config.get('_cleanup_initialized',False)})
@main.route('/api/separate',methods=['POST'])
def separate_audio():
 if'file'not in request.files:return jsonify({"error":"No file provided"}),400
 file=request.files['file']
 if file.filename=='':return jsonify({"error":"No file selected"}),400
 if not allowed_file(file.filename):return jsonify({"error":f"Unsupported file type. Allowed: {separator.supported_formats}"}),400
 start_time=request.form.get('start_time',type=float,default=None);end_time=request.form.get('end_time',type=float,default=None)
 stems=request.form.get('stems',default='["vocals","drums","bass","other"]')
 try:
  import json
  stems_list=json.loads(stems)
  if not isinstance(stems_list,list)or len(stems_list)==0:
   stems_list=['vocals','drums','bass','other']
 except:
  stems_list=['vocals','drums','bass','other']
 if start_time is not None and end_time is not None:
  if start_time<0:start_time=0
  if end_time<=start_time:return jsonify({"error":"End time must be greater than start time"}),400
  if end_time-start_time<0.1:return jsonify({"error":"Trim segment must be at least 0.1 seconds"}),400
 output_format='mp3';quality='high';job_id=str(uuid.uuid4());filename=secure_filename(file.filename);upload_path=os.path.normpath(os.path.join(current_app.config['UPLOAD_FOLDER'],f"{job_id}_{filename}"));file.save(upload_path)
 try:result=separator.separate_audio(upload_path,job_id,output_format,quality,start_time,end_time,stems_list);return jsonify(result)
 except Exception as e:return jsonify({"error":str(e),"job_id":job_id}),500
@main.route('/api/download/<job_id>/<track_name>',methods=['GET'])
def download_track(job_id,track_name):
 try:
  requested_format=request.args.get('format','mp3').lower()
  if requested_format not in separator.format_mime_types:requested_format='mp3'
  results_folder=current_app.config['RESULTS_FOLDER'];file_path=os.path.normpath(os.path.join(results_folder,job_id,f"{track_name}.{requested_format}"))
  if not os.path.exists(file_path):
   for fmt in separator.format_mime_types.keys():
    alt_path=os.path.normpath(os.path.join(results_folder,job_id,f"{track_name}.{fmt}"))
    if os.path.exists(alt_path):file_path=alt_path;requested_format=fmt;break
   else:return jsonify({"error":f"File '{track_name}' not found in any format for job {job_id}"}),404
  file_size=os.path.getsize(file_path)
  response=send_file(file_path,as_attachment=True,download_name=f"{track_name}.{requested_format}",mimetype=separator.format_mime_types[requested_format])
  response.headers.add('Access-Control-Allow-Origin','*');response.headers.add('Content-Length',str(file_size));response.headers.add('X-File-Format',requested_format.upper());response.headers.add('X-Quality','320kbps'if requested_format=='mp3'else'Professional');response.headers.add('Cache-Control','no-cache, no-store, must-revalidate');response.headers.add('Pragma','no-cache');response.headers.add('Expires','0')
  return response
 except Exception as e:return jsonify({"error":f"Download failed: {str(e)}"}),500
@main.route('/api/jobs/<job_id>/status',methods=['GET'])
def job_status(job_id):
 results_dir=os.path.normpath(os.path.join(current_app.config['RESULTS_FOLDER'],job_id))
 if os.path.exists(results_dir):
  files=os.listdir(results_dir)
  if files:
   stems={}
   for f in files:
    if'.'in f:
     name,ext=f.rsplit('.',1)
     if name not in stems:stems[name]=[]
     stems[name].append(ext)
   audio_urls={}
   for stem_name,formats in stems.items():audio_urls[stem_name]={"formats":formats,"urls":{fmt:f"/audio/{job_id}/{stem_name}.{fmt}"for fmt in formats}}
   return jsonify({"job_id":job_id,"status":"completed","stems":stems,"audio_urls":audio_urls,"file_count":len(files),"quality":"high","note":"Professional 320kbps processing complete"})
 upload_dir=current_app.config['UPLOAD_FOLDER']
 for file in os.listdir(upload_dir):
  if file.startswith(job_id):return jsonify({"job_id":job_id,"status":"processing","message":"Audio is being processed with professional quality","quality":"high"})
 return jsonify({"error":"Job not found"}),404
@main.route('/api/formats',methods=['GET'])
def available_formats():
 return jsonify({"formats":[{"name":"mp3","display":"MP3","description":"320kbps Professional Audio","qualities":[{"name":"high","bitrate":"320kbps","description":"Studio Quality"},{"name":"medium","bitrate":"192kbps","description":"Good quality"},{"name":"low","bitrate":"128kbps","description":"Standard quality"}]},{"name":"wav","display":"WAV","description":"24-bit Uncompressed Studio Master","qualities":[{"name":"high","description":"24-bit, 48kHz Professional"},{"name":"medium","description":"16-bit, 44.1kHz CD Quality"},{"name":"low","description":"16-bit, 22.05kHz"}]},{"name":"flac","display":"FLAC","description":"Lossless Professional Archive","qualities":[{"name":"high","description":"Maximum compression (studio quality)"},{"name":"medium","description":"Good compression"},{"name":"low","description":"Fast compression"}]}],"default_quality":"high","default_format":"mp3","note":"All processing uses 320kbps MP3 professional quality"})
@main.route('/api/debug/audio-paths/<job_id>',methods=['GET'])
def debug_audio_paths(job_id):
 results_dir=os.path.normpath(os.path.join(current_app.config['RESULTS_FOLDER'],job_id))
 if not os.path.exists(results_dir):return jsonify({"error":f"Job directory not found: {results_dir}","results_folder":current_app.config['RESULTS_FOLDER'],"job_id":job_id}),404
 files=[]
 for f in os.listdir(results_dir):
  file_path=os.path.join(results_dir,f);files.append({"name":f,"path":file_path,"exists":os.path.exists(file_path),"size":os.path.getsize(file_path)if os.path.exists(file_path)else 0,"url":f"/audio/{job_id}/{f}"})
 return jsonify({"job_id":job_id,"results_dir":results_dir,"files_count":len(files),"files":files})
@main.route('/api/trim/test',methods=['POST'])
def test_trim():
 if'file'not in request.files:return jsonify({"error":"No file provided"}),400
 file=request.files['file']
 if file.filename=='':return jsonify({"error":"No file selected"}),400
 return jsonify({"message":"Trim test endpoint active","filename":file.filename,"trim_sample":{"start_time":5.0,"end_time":15.0,"duration":10.0},"note":"This endpoint demonstrates the trim functionality"})
@main.route('/api/storage/health',methods=['GET'])
def storage_health():
 return jsonify({"status":"healthy","service":"slice-lemonade","endpoints":{"health":"/api/health","separate":"/api/separate","download":"/api/download/{job_id}/{track_name}","job_status":"/api/jobs/{job_id}/status","formats":"/api/formats","storage_stats":"/api/storage/stats","debug_paths":"/api/debug/audio-paths/{job_id}"}})