import cv2
import numpy as np

DENSITY29_WS = np.array(["Ñ","@","#","W","$","9","8","7","6","5","4","3","2","1","0","?","!","a","b","c",";",":","+","=","-",",",".","_"," "])
DENSITY29_BS = np.flip(DENSITY29_WS)
DENSITY29_BS_EXTEND = np.concatenate((DENSITY29_BS, np.array(["Ñ","Ñ","Ñ","Ñ","Ñ","Ñ","Ñ","Ñ","Ñ","Ñ"])))

DENSITY70_WS = np.array(["$","@","B","%","8","&","W","M","#","*","o","a","h","k","b","d","p","q","w","m","Z","O","0","Q","L","C","J","U","Y","X","z","c","v","u","n","x","r","j","f","t","/","\\","|","(",")","1","{","}","[","]","?","-","_","+","~","<",">","i","!","l","I",";",":",",","\",""^","`","'","."," "])
DENSITY70_BS = np.flip(DENSITY29_WS)
DENSITY = [DENSITY70_WS, DENSITY70_BS, DENSITY29_WS, DENSITY29_BS, DENSITY29_BS_EXTEND]

def generate_empty_image(width, heigth):
    return np.zeros((heigth, width, 1), dtype=np.uint8)

def frame2ascii(frame, density_type):
    matrix = map(np.asarray(frame), 0, 255, 0, len(DENSITY[density_type])-1).astype(int)
    ascii_frame = np.array(DENSITY[density_type][matrix], dtype=str)
    return ascii_frame

def map(lum, smin, smax, fmin, fmax):
    scale = (fmax - fmin) / (smax - smin)
    return lum*scale

def ascii_formatter(ascii_frame, img, scale_ascii, scale_display):
    for line in range(len(ascii_frame)):
        for col in range(len(ascii_frame[0])):
            cv2.putText(img=img, text=ascii_frame[line][col], org=(col*scale_ascii//scale_display,line*scale_ascii//scale_display), fontFace=cv2.FONT_HERSHEY_COMPLEX_SMALL, fontScale=scale_ascii/(20*scale_display), color=(255,255,255))

def save_ImageSequence(frame, name, extention, frame_count, path=''):
    cv2.imwrite(path+name+"_"+str(frame_count)+"."+extention, frame)

def loadVideo():
    path = input('What is the path of your video: ')
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("\nFPS: ", fps)
    print("Width: ", width)
    print("Height: ", height)

    return cap, width, height

def options():
    scale_ascii = int(input('\nChoose the scale of the ASCII characters (default 8): '))
    scale_display = input('Choose the scale factor of the display output (default 1.0): ')
    density_type = int(input('Choose between the available density type:\n\
    0 - 70_WhiteScreen\n\
    1 - 70_BlackScreen\n\
    2 - 29_WhiteScreen\n\
    3 - 29_BlackScreen\n\
    4 - 29_BlackScreen_whiteplus10\n\
    >> '))
    contrast = float(input('Choose the contrast(default 1.2): '))
    show_output = True if input('Show output? (Y or N): ') in ['Y', 'Yes', 'yes', 'y'] else False
    save = True if input('Show output? (Y or N): ') in ['Y', 'Yes', 'yes', 'y'] else False

    return scale_ascii, scale_display, density_type, contrast, show_output, save

def outputInfo():
    sequence_name = str(input('Name format of your output sequence: '))
    sequence_path = str(input('Ouput path of your sequence: '))
    return sequence_name, sequence_path

def ASCIIGenerator(cap, density_type, scale_ascii, scale_display, show_output=True, save=False, sequence_name=None, sequence_path=None):
    if not cap.isOpened():
        print("Cannot open camera/video file")
        exit()

    frame_count = 0

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        image = cv2.resize(frame, (new_width, new_height))

        brightness = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        img = generate_empty_image(width_display, height_display)

        ascii_frame = frame2ascii(brightness, density_type)
        ascii_formatter(ascii_frame, img,  scale_ascii, scale_display)

        if save:
            save_ImageSequence(img, sequence_name, 'png', frame_count, sequence_path)
        
        if show_output:
            cv2.imshow('frame', img)

        if cv2.waitKey(1) == ord('q'):
            break
        
        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    sequence_name = None
    sequence_path = None

    cap, width, height = loadVideo()
    scale_ascii, scale_display, density_type, contrast, show_output, save = options()

    if save:
        sequence_name, sequence_path = outputInfo()

    aspect_ratio = height / width
    new_width = width//scale_ascii
    new_height = int(aspect_ratio * new_width)
    width_display = width//scale_display
    height_display = int(aspect_ratio * width_display)


    print("\nWidth Display: ", width_display)
    print("Height Display: ", height_display)
    print('')

    ASCIIGenerator(cap, density_type, scale_ascii, scale_display, show_output, save, sequence_name, sequence_path)