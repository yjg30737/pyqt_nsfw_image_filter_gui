# pyqt_nsfw_image_filter_gui
Yup.

You need two packages

nsfw-detector and PyQt5

This works every images, not only real photo but paintings such as anime too.

## How to Run
1. clone this
2. pip install -r requirements.txt
3. install [Keras 299x299 Image Model](https://s3.amazonaws.com/ir_public/ai/nsfw_models/nsfw.299x299.h5) and put it into src folder
4. python main.py

## Preview
![image](https://github.com/yjg30737/pyqt_nsfw_image_filter_gui/assets/55078043/f19099ec-32fc-49af-8552-2db195801935)

### How to Use
1. Set the directory which contains image files.
2. Press the filter button to remove the NSFW images.

## How this works
This is using [Keras 299x299 Image Model](https://s3.amazonaws.com/ir_public/ai/nsfw_models/nsfw.299x299.h5), and this is influenced by <a href="https://github.com/GantMan/nsfw_model">nsfw_model</a> also known as nsfw-detector. This is pretty much GUI version of it.

Personally i categorized nsfw level as three, "nsfw", "semi-nsfw", "safe" based on certain standard.

## Note
You can use this in CUI(Python code) only. Look at the script.py to figure it out how it works.

This really helps me a lot from encountered embarrassing moment from someone who checks my images which stored by crawling 🙂

By the way i'm not sure i can upload the even slightly controversial image to explain how this works so i won't do it.

Please try it !!
