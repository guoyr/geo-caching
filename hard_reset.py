from pymongo import MongoClient

def main():
	c = MongoClient()
	c.drop_database("image_db")
	c.drop_database("image_info_db")

if __name__ == '__main__':
	main()