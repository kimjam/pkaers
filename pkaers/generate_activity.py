import pandas as pd
from datetime import datetime


def generate_activity(student,
					  map_data,
					  khanstudent,
					  exerstates,
					  itemdiffs):
	"""
	student list of dictionaries containing student info
	map_data list of dictionaries containing student's Math MAP records
	khanstudent list of dictionaries containing student's khan info
	exerstates list of dictionaries containing exercise state changes
	itemdiffs list of dicionaries containing prior item difficulty estimates
	"""

	student_df = pd.DataFrame(student)
	map_df = pd.DataFrame(map_data)
	khanstudent_df = pd.DataFrame(khanstudent)
	exerstates_df = pd.DataFrame(exerstates)
	itemdiffs_df = pd.DataFrame(itemdiffs)

	def clean_dates(df):
		cols = df.select_dtypes(include=['datetime64[ns, UTC]']).columns
		for i in range(len(cols)):
			df[cols[i]] = df[cols[i]].apply(lambda x: x.replace(tzinfo=None))

		return df

	student_df = clean_dates(student_df)
	map_df = clean_dates(map_df)
	khanstudent_df = clean_dates(khanstudent_df)
	exerstates_df = clean_dates(exerstates_df)
	itemdiffs_df = clean_dates(itemdiffs_df)

	cutoff_date = itemdiffs_df['last_updated'][0]
	# filter out activity before cutoff_date

	states_wide = pd.DataFrame(columns=['exercise', 'mastery1', 'mastery2',
										'mastery3', 'practiced', 'student'])

	for stu in list(set(exerstates_df['student'].tolist())):
		state = exerstates_df[exerstates_df['student'] == stu]
		state_wide = state.pivot(index='exercise',
								 columns='exercise_status',
								 values='date')

		state_wide.reset_index(level=0, inplace=True)
		state_wide['student'] = stu
		states_wide = states_wide.append(state_wide)
