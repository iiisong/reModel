
from stabledesign import stabledesign
from PIL import Image
import time

def main():
    base_img = "test_data/input_img.png"
    gen_img_path = "test_data/OUTPUT.png"
    prompt = 'Cottage core college dorm for a plant and book lover.'

    i = 0
    while True :
        input_image = Image.open(base_img)

        output = stabledesign(input_image, prompt, optimize=False)

        print('Sleeping for 3...')
        time.sleep(5)
        print('Waking up...')

        print(f'Iteration No. {i}')
        if i % 5 == 0 :
            print('Saved img')
            output.save(gen_img_path)
        i += 1

if __name__ == "__main__":
    main()