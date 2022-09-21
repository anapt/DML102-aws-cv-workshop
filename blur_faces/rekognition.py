import boto3
import time

def boto3_client():
    return boto3.client('rekognition')


def check_format_and_size(filename, size):
    if filename.split('.')[-1] in ['mp4', 'mov']:
        if size < 10*1024*1024*1024:
            return True
    return False

def start_face_detection(bucket, video, size, reko_client=None):
    assert check_format_and_size(video, size)
    if reko_client == None:
        reko_client = boto3.client('rekognition')
    response = reko_client.start_face_detection(Video={'S3Object': {'Bucket': bucket, 'Name': video}})
    return response['JobId']

def wait_for_completion(job_id, wait_time_in_s=30, reko_client=None):
    if reko_client == None:
        reko_client = boto3.client('rekognition')
    response = reko_client.get_face_detection(JobId=job_id)
    while (response['JobStatus'] == 'IN_PROGRESS'):
        print('.', end='')
        time.sleep(wait_time_in_s)
        response = reko_client.get_face_detection(JobId=job_id)
    print('Complete')
    return response

def get_timestamps_and_faces(response, job_id, reko_client=None):
    final_timestamps = {}
    next_token = "Y"
    first_round = True
    while next_token != "":
        print('.', end='')
        # Set some variables if it's the first iteration
        if first_round:
            next_token = ""
            first_round = False
        # Query Reko Video
        response = reko_client.get_face_detection(JobId=job_id, NextToken=next_token)
        # Iterate over every face
        for face in response['Faces']:
            f = face["Face"]["BoundingBox"]
            t = str(face["Timestamp"])
            time_faces = final_timestamps.get(t)
            if time_faces == None:
                final_timestamps[t] = []
            final_timestamps[t].append(f)
        # Check if there is another portion of the response
        try:
            next_token = response['NextToken']
        except:
            break
    # Return the final dictionary
    print('Complete')
    return final_timestamps