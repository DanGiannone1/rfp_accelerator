import threading

# Dictionary to store in-progress uploads
in_progress_uploads = {}

# Set to store completed uploads
completed_uploads = set()

# Dictionary to store upload errors
upload_errors = {}

# Lock for thread-safe operations
upload_lock = threading.Lock()

def add_in_progress_upload(filename):
    with upload_lock:
        in_progress_uploads[filename] = 'Processing'

def remove_in_progress_upload(filename):
    with upload_lock:
        if filename in in_progress_uploads:
            del in_progress_uploads[filename]
        completed_uploads.add(filename)

def set_upload_error(filename):
    with upload_lock:
        if filename in in_progress_uploads:
            del in_progress_uploads[filename]
        upload_errors[filename] = 'Error'

def get_all_rfps():
    with upload_lock:
        all_rfps = [
            {"name": filename, "status": "Processing"} 
            for filename in in_progress_uploads
        ] + [
            {"name": filename, "status": "Complete"} 
            for filename in completed_uploads
        ] + [
            {"name": filename, "status": "Error"} 
            for filename in upload_errors
        ]
        return all_rfps

def clear_completed_uploads():
    with upload_lock:
        completed_uploads.clear()

def has_in_progress_uploads():
    with upload_lock:
        return len(in_progress_uploads) > 0