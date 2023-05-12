from fastapi import FastAPI, File
from stability_sdk.api import Context
from stability_sdk.animation import AnimationArgs, Animator
from stability_sdk.utils import create_video_from_frames
import stability_sdk
# from stability_sdk.exceptions import ClassifierException, OutOfCreditsException
from tqdm import tqdm
import shutil
import os
import io
from PIL import Image


#Install
#pip install 'stability_sdk[anim_ui]' # install the animation SDK

#Run
#python -m stability_sdk animate --gui # launch the UI

# Set up the API context
STABILITY_HOST = "grpc.stability.ai:443"
STABILITY_KEY =os.environ.get("STABILITY_KEY")

context = Context(STABILITY_HOST, STABILITY_KEY)

# Configure the animation
args = AnimationArgs()
args.interpolate_prompts = True
args.locked_seed = True
args.max_frames = 48
args.seed = 42
args.strength_curve = "0:(0)"
args.diffusion_cadence_curve = "0:(4)"
args.cadence_interp = "film"

animation_prompts = {
    0: "a photo of a cute cat",
    24: "a photo of a cute dog",
}
negative_prompt = ""

# Create an instance of the Animator class
animator = Animator(
    api_context=context,
    animation_prompts=animation_prompts,
    negative_prompt=negative_prompt,
    args=args,
    out_dir="video_01"
)

# Create a FastAPI app
app = FastAPI()

# Endpoint to generate a video
@app.post("/generate_video")
async def generate_video(file: bytes = File(...)):
    try:
        # Load the image from the uploaded file
        image = Image.open(io.BytesIO(file)).convert("RGB")

        # Process the image and generate the animation prompts
        animation_prompts = {
            0: "a photo of a cute kit",  
            24: "a photo of a cute bird", 
            64: "a photo of a cute bear", 
        }

        # Update the animator with the new prompts and image
        animator.animation_prompts = animation_prompts
        animator.input_image = image

        # Render the animation frames
        for _ in tqdm(animator.render(), total=args.max_frames):
            pass

        # Create a video from the frames
        create_video_from_frames("video_01", "animation_video.mp4")

        # Clean up temporary files
        shutil.rmtree("video_01")

        return {"message": "Video generated successfully."}

    except stability_sdk.api.OutOfCreditsException as e:
        # Log the error message
        print(f"Error: {str(e)}")

        # Return a user-friendly message
        return {"message": "Sorry, your organization does not have enough balance to request this action. Please top up your balance and try again."}


import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

