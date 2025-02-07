import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import dotenv
import os
import shutil
import time

dotenv.load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


class S3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name):
        self.s3 = boto3.client(
            "s3",
            endpoint_url="https://s3.cloud.ru",  # Исправленный эндпоинт
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="ru-central-1",  # Указываем регион
            config=boto3.session.Config(
                signature_version="s3v4"
            ),  # Включаем подпись v4
        )
        self.bucket_name = bucket_name

    def download_file(self, s3_key, local_path):
        try:
            self.s3.download_file(self.bucket_name, s3_key, local_path)
            return True
        except FileNotFoundError:
            print("Указанный файл не найден")
        except NoCredentialsError:
            print("Не предоставлены учетные данные")
        except PartialCredentialsError:
            print("Учетные данные неполные")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_sounds_pack(self, name: str):
        try:
            pack_path = f"./assets/sounds/{name}"
            if name in os.listdir("./assets/sounds"):
                shutil.rmtree(f"./assets/sounds/{name}")
            os.mkdir(pack_path)
            os.mkdir(pack_path + "/ingame_music")
            os.mkdir(pack_path + "/replics")
            for key in self.s3.list_objects(
                Bucket=self.bucket_name, Prefix=f"modules/sounds/{name}/"
            )["Contents"]:
                key = key["Key"]
                print(key)
                path_parts = key.split("/")
                if "." in path_parts[-1]:
                    if "ingame_music" in path_parts:
                        self.download_file(
                            key, pack_path + "/ingame_music/" + path_parts[-1]
                        )
                    elif "replics" in path_parts:
                        self.download_file(
                            key, pack_path + "/replics/" + path_parts[-1]
                        )
                    else:
                        self.download_file(key, pack_path + "/" + path_parts[-1])
            return True
        except Exception as E:
            if name in os.listdir("./assets/sounds"):
                shutil.rmtree(f"./assets/sounds/{name}")
            return False

    def get_balls_patterns_pack(self, name: str):
        try:
            if name + ".json" in os.listdir("./assets/balls patterns"):
                os.remove("./assets/balls patterns/" + name + ".json")
            self.download_file(
                "modules/balls_patterns/" + name + ".json",
                "./assets/balls patterns/" + name + ".json",
            )
            return True
        except:
            if name + ".json" in os.listdir("./assets/balls patterns"):
                os.remove("./assets/balls patterns/" + name + ".json")
            return False

    def get_loading_screen_pack(self, name: str):
        try:
            if name + ".png" in os.listdir("./assets/loading screen"):
                os.remove("./assets/loading screen/" + name + ".png")
            self.download_file(
                "modules/loading_screens/" + name + ".png",
                "./assets/loading screen/" + name + ".png",
            )
            return True
        except:
            if name + ".png" in os.listdir("./assets/loading screen"):
                os.remove("./assets/loading screen/" + name + ".png")
            return False

    def get_table_pattern(self, name: str):
        try:
            if name + ".png" in os.listdir("./assets/table patterns"):
                os.remove("./assets/table patterns/" + name + ".png")
            self.download_file(
                "modules/table patterns/" + name + ".png",
                "./assets/table patterns/" + name + ".png",
            )
            return True
        except:
            if name + ".png" in os.listdir("./assets/table patterns"):
                os.remove("./assets/table patterns/" + name + ".png")
            return False

    def get_pack(self, module):
        match module["type"]:
            case "sounds":
                self.get_sounds_pack(module["name"])
            case "balls patterns":
                self.get_balls_patterns_pack(module["name"])
            case "loading screen":
                self.get_loading_screen_pack(module["name"])
            case "table pattern":
                self.get_table_pattern(module["name"])

    def update_packs_data(self):
        try:
            self.download_file("packs_data.json", "./data/packs_data.json")
        except Exception as e:
            return e


s3client = S3Client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME)
