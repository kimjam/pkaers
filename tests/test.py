# flake8: noqa
import pandas as pd
from pkaers.khan_elo import khan_elo
import unittest


class ObjectTest(unittest.TestCase):
	def configure(self):
		self.student = pd.read_csv('student.csv').T.to_dict().values()
		self.map_data = pd.read_csv('map.csv').T.to_dict().values()
		self.khanstudent = pd.read_csv('khanstudent.csv').T.to_dict().values()
		self.exerstates = pd.read_csv('exerstates.csv').T.to_dict().values()
		selfkhanpred = []


class StudentTest(ObjectTest):
	def setUp(self):
		self.configure()


	def test_studentpredict(self):
		predict = khan_elo(
			student=self.student,
			map_data=self.map_data,
			khanstudent=self.khanstudent,
			exerstates=self.exerstates,
			update='students',
			khanpred=self.khanpred)

		self.assertEqual(len(predict), 2)
		self.assertEqual(predict[0]['rit_prediction'], None)


class ExerciseTest(ObjectTest):
	def setUp(self):
		self.configure()

	def test_exerciseupdate(self):
		items = khan_elo(
			student=self.student,
			map_data=self.map_data,
			khanstudent=self.khanstudent,
			exerstates=self.exerstates,
			update='items')

		self.assertEqual(len(items), 1124)
		sample = [
			item['matches']
			for item in items
			if item['slug'] == 'adding_and_subtracting_negative_numbers'
		][0]
		self.assertEqual(sample, 1)

