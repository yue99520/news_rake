import os
from dotenv import load_dotenv

load_dotenv()

def main():
  print(os.getenv('MODEL_API_KEY'))
# test os getenv
if __name__ == '__main__':
  main()