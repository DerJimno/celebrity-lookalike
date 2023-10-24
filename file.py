import argparse
parser = argparse.ArgumentParser(description="Find the most common celebrity name from a list of image URLs.")
parser.add_argument('--pat', required=True)
parser.add_argument('--file', required=True)

from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2

if __name__ == '__main__':
    args = parser.parse_args()
    PAT = args.pat
    file_path = args.file
# Specify the correct user_id/app_id pairings
# Since you're making inferences outside your app's scope
USER_ID = 'clarifai'
APP_ID = 'main'
# Change these to whatever model and image URLs you want to use
MODEL_ID = 'celebrity-face-detection'
MODEL_VERSION_ID = '2ba4d0b0e53043f38dbbed49e03917b6'

# Read the list of URLs from a file
with open(file_path, 'r') as file:
    IMAGE_URLS = [line.strip() for line in file.readlines() if line.strip()]


channel = ClarifaiChannel.get_grpc_channel()
stub = service_pb2_grpc.V2Stub(channel)

metadata = (('authorization', 'Key ' + PAT),)

userDataObject = resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID)

# Create a dictionary to store celebrity name counts
celebrity_counts = {}

for IMAGE_URL in IMAGE_URLS:
    post_model_outputs_response = stub.PostModelOutputs(
        service_pb2.PostModelOutputsRequest(
            user_app_id=userDataObject,
            model_id=MODEL_ID,
            version_id=MODEL_VERSION_ID,
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            url=IMAGE_URL
                        )
                    )
                )
            ]
        ),
        metadata=metadata
    )
    if post_model_outputs_response.status.code != status_code_pb2.SUCCESS:
        print(post_model_outputs_response.status)
        raise Exception("Post model outputs failed, status: " + post_model_outputs_response.status.description)

    # Since we have one input, one output will exist here
    output = post_model_outputs_response.outputs[0]

    if output.data.regions[0].data.concepts:
        # Get the name of the first celebrity detected
        celebrity_name = output.data.regions[0].data.concepts[0].name

        # Update the count in the dictionary
        celebrity_counts[celebrity_name] = celebrity_counts.get(celebrity_name, 0) + 1

# Find the celebrity name with the highest count
most_common_celebrity = max(celebrity_counts, key=celebrity_counts.get)

print(most_common_celebrity)
