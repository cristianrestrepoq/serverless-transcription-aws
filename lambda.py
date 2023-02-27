import json
import boto3
import urllib

s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')

def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    s3_file_name = event['Records'][0]['s3']['object']['key']
    audio_file = '/tmp/{}'.format(s3_file_name)
    object_url = f"s3://{bucket_name}/{s3_file_name}"

    transcribe_job_name = 'Test_transcription1'
    
    transcribe = boto3.client('transcribe')
    response = transcribe.start_transcription_job(
        TranscriptionJobName=transcribe_job_name,
        #IdentifyLanguage = True,
        LanguageCode='fr-FR',
        MediaFormat='mp4',
        Media={
            'MediaFileUri': object_url
        }
    )
    
    while True:
        final_response = transcribe.get_transcription_job(TranscriptionJobName=transcribe_job_name)
        if final_response['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        
    transcription_url = final_response["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    transcription_file = urllib.request.urlopen(transcription_url).read().decode("utf-8")
    transcription = json.loads(transcription_file)["results"]["transcripts"][0]["transcript"]
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'{transcription}')
    }