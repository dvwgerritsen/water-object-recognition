def predict(file_path, show_image):
    # import the necessary packages
    from imagesearch import config
    from torchvision import transforms
    import imutils
    import pickle
    import torch
    import cv2
    from random import randrange

    # # construct the argument parser and parse the arguments
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--input", required=True,
    # 	help="path to input image/text file of image paths")
    # args = vars(ap.parse_args())
    #
    # # determine the input file type, but assume that we're working with
    # # single input image
    # filetype = mimetypes.guess_type(args["input"])[0]
    # imagePaths = [args["input"]]
    # # if the file type is a text file, then we need to process *multiple*
    # # images
    # if "text/plain" == filetype:
    # 	# load the image paths in our testing file
    # 	imagePaths = open(args["input"]).read().strip().split("\n")
    #
    # 	# load our object detector, set it evaluation mode, and label
    # 	# encoder from disk
    print("[INFO] loading object detector...")
    # map_location=cpu is required to use a model created with a gpu on the cpu.
    model = torch.load(config.MODEL_PATH, map_location='cpu').to(config.DEVICE)
    model.eval()
    le = pickle.loads(open(config.LE_PATH, "rb").read())
    # define normalization transforms
    transforms = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor(),
        transforms.Normalize(mean=config.MEAN, std=config.STD)
    ])


    # loop over the images that we'll be testing using our bounding box
    # regression model
    # load the image, copy it, swap its colors channels, resize it, and
    # bring its channel dimension forward
    image = cv2.imread(file_path)
    orig = image.copy()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (224, 224))
    image = image.transpose((2, 0, 1))
    # convert image to PyTorch tensor, normalize it, flash it to the
    # current device, and add a batch dimension
    image = torch.from_numpy(image)
    image = transforms(image).to(config.DEVICE)
    image = image.unsqueeze(0)

    # predict the bounding box of the object along with the class
    # label
    (boxPreds, labelPreds) = model(image)
    (startX, startY, endX, endY) = boxPreds[0]
    # determine the class label with the largest predicted
    # probability
    labelPreds = torch.nn.Softmax(dim=-1)(labelPreds)
    i = labelPreds.argmax(dim=-1).cpu()
    label = le.inverse_transform(i)[0]

    # resize the original image such that it fits on our screen, and
    # grab its dimensions
    orig = imutils.resize(orig, width=600)
    (h, w) = orig.shape[:2]
    # scale the predicted bounding box coordinates based on the image
    # dimensions
    startX = int(startX * w)
    startY = int(startY * h)
    endX = int(endX * w)
    endY = int(endY * h)
    # draw the predicted bounding box and class label on the image
    y = startY - 10 if startY - 10 > 10 else startY + 10
    cv2.putText(orig, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 255, 0), 2)
    cv2.rectangle(orig, (startX, startY), (endX, endY),
                  (0, 255, 0), 2)
    if show_image:
        # show the output image
        cv2.imshow("Output", orig)
        cv2.waitKey(0)

    file_name = str(randrange(100000000)) + ".jpg"
    cv2.imwrite("predicted_images/" + file_name, orig)

    return file_name

if __name__ == '__main__':
    predict(r"C:\Users\koenh\IdeaProjects\water-object-recognition\data\resized_Images\000000_jpg.rf.beffaf3b548106ccf1da5dc629bc9504.jpg", True)
