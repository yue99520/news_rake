import os
from dotenv import load_dotenv

load_dotenv()
def platform_img(name: str) -> str:
    # use a dict to store the image url
    imgList = {
        'followin': 'https://play-lh.googleusercontent.com/GTpsvKFZZ0cv5_au5LciVcrEWEVe6_P1xUj47wz0QgwUuHF93ZvojTW1Uj19nJxIBq4',
    }
    return imgList.get(name, 'https://example.com')
def main():
  print(os.getenv('MODEL_API_KEY'))
# test os getenv
if __name__ == '__main__':
  main()
  print(platform_img('followin'))