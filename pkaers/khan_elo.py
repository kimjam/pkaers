import pandas as pd
from datetime import datetime
from math import exp


def khan_elo(
        student,
        map_data,
        khanstudent,
        exerstates,
        itemdiffs,
        khanpred,
        update):
    """
    student list of dictionaries containing student info
    map_data list of dictionaries containing student's Math MAP records
    khanstudent list of dictionaries containing student's khan info
    exerstates list of dictionaries containing exercise state changes
    itemdiffs list of dictionaries containing prior item difficulty estimates
    khanpred list of dictionaries containg khan based RIT predictions
    update set to 'items' to update item difficulties and 'students' to update
    student proficiencies
    """

    student_df = pd.DataFrame(student)
    map_df = pd.DataFrame(map_data)
    khanstudent_df = pd.DataFrame(khanstudent)
    exerstates_df = pd.DataFrame(exerstates)
    itemdiffs_df = pd.DataFrame(itemdiffs)
    khanpred_df = pd.DataFrame(khanpred)

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
    khanpred_df = clean_dates(khanpred_df)

    if update == 'items':
        cutoff_date = itemdiffs_df['last_updated'][0]
        # filter out map scores after cutoff_date, add email,
        # khan student user_id
        map_df = map_df[map_df['date_taken'] <= cutoff_date]

        map_df = pd.merge(map_df,
                          student_df[['id', 'email']],
                          left_on='student_id',
                          right_on='id',
                          how='left')

        map_df = pd.merge(map_df,
                          khanstudent_df[['identity_email', 'student']],
                          left_on='email',
                          right_on='identity_email',
                          how='left')

        map_df = map_df.groupby('student').agg(
            lambda x: x.iloc[x.date_taken.values.argmax()]
        )

        map_df.reset_index(level=0, inplace=True)
        exerstates_df = exerstates_df[exerstates_df['date'] >= cutoff_date]
    elif update == 'students':
        map_df = pd.merge(map_df,
                          student_df[['id', 'email']],
                          left_on='student_id',
                          right_on='id',
                          how='left')

        map_df = pd.merge(map_df,
                          khanstudent_df[['identity_email', 'student']],
                          left_on='email',
                          right_on='identity_email',
                          how='left')

        map_df = map_df.groupby('student').agg(
            lambda x: x.iloc[x.date_taken.values.argmax()]
        )

        map_df.reset_index(level=0, inplace=True)

    states_wide = pd.DataFrame(
        columns=[
            'exercise', 'mastery1', 'mastery2',
            'mastery3', 'practiced', 'student']
    )

    for stu in khanstudent_df['student'].tolist():
        if update == 'students':
            cutoff_date = None
            if not khanpred_df.empty:
                cutoff_date = khanpred_df['last_updated'][
                    khanpred_df.student == stu
                ].tolist()[0]

            if not cutoff_date:
                cutoff_date = map_df['date_taken'][map_df.student == stu].\
                    tolist()[0]

        state = exerstates_df[
            (exerstates_df.student == stu) &
            (exerstates_df.date >= cutoff_date)
        ]
        state_wide = state.pivot(
            index='exercise',
            columns='exercise_status',
            values='date'
        )

        state_wide.reset_index(level=0, inplace=True)
        state_wide['student'] = stu
        states_wide = states_wide.append(state_wide)

    states_wide = pd.merge(
        states_wide,
        itemdiffs_df,
        left_on='exercise',
        right_on='slug',
        how='left'
    )

    states_wide = pd.merge(
        states_wide,
        map_df[['student', 'scale_score']],
        on='student',
        how='left'
    )

    states_wide['item_win'] = states_wide.mastery3.isnull().apply(
        lambda x: int(x)
    )

    states_wide['student_win'] = states_wide.mastery3.isnull().apply(
        lambda x: int(not x)
    )

    states_wide['scale_score'] = states_wide['scale_score'].apply(
        lambda x: float(x)
    )

    if update == 'items':
        for slug in itemdiffs_df['slug'].tolist():
            opponents = states_wide[states_wide.exercise == slug]
            diff = itemdiffs_df[itemdiffs_df.slug == slug]['rit_estimate']
            diff = diff.tolist()[0]
            matches = itemdiffs_df[itemdiffs_df.slug == slug]['matches']
            matches = matches.tolist()[0]
            if len(opponents) == 0:
                continue
            else:
                opponents['scale_score'] = opponents['scale_score'].apply(
                    lambda x: (x - 200) / 10
                )
                itemdiffs_df.loc[:, 'matches'][itemdiffs_df.slug == slug] += (
                    matches
                )
                diff = (diff - 200) / 10
                if (matches + len(opponents)) > 100:
                    W = .02
                elif (matches + len(opponents)) > 50:
                    W = .04
                else:
                    W = .2

                for i in range(len(opponents)):
                    diff += (
                        W * (
                            opponents.iloc[i]['item_win'] -
                            (
                                exp(diff - opponents.iloc[i]['scale_score']) /
                                (
                                    1 +
                                    exp(
                                        diff -
                                        opponents.iloc[i]['scale_score']
                                    )
                                )
                            )
                        )
                    )

                itemdiffs_df.loc[:, 'rit_estimate'][itemdiffs_df.slug == slug]\
                    = round(diff * 10 + 200, 2)

        return itemdiffs_df.to_dict('records')

    elif update == 'students':
        predictions = []
        for student in khanstudent_df['student'].tolist():
            opponents = states_wide[states_wide.student == student]
            start_est = float(
                map_df[map_df.student == student]['scale_score'].tolist()[0]
            )
            matches = float(len(opponents))
            if len(opponents) == 0:
                predictions.append({
                    'student': student,
                    'rit_prediction': None,
                    'last_updated': datetime.now()
                })
            else:
                if (sum(opponents['student_win']) / matches) >= 0.8:
                    opponents['scale_score'] = opponents['scale_score'].apply(
                        lambda x: (x - 200) / 10
                    )

                    opponents['rit_estimate'] = opponents['rit_estimate'].\
                        apply(
                            lambda x: (x - 200) / 10
                        )
                    start_est = (start_est - 200) / 10
                    for i in range(len(opponents)):
                        spread = abs(
                            start_est - opponents.iloc[i]['rit_estimate']
                        )
                        if spread >= .2:
                            W = 0.2
                        else:
                            W = 0.05

                        start_est += (
                            W * (
                                opponents.iloc[i]['student_win'] -
                                (
                                    exp(
                                        start_est -
                                        opponents.iloc[i]['rit_estimate']
                                    ) / (
                                        1 +
                                        exp(
                                            start_est -
                                            opponents.iloc[i]['rit_estimate']
                                        )
                                    )
                                )
                            )
                        )

                    predictions.append({
                        'student': student,
                        'rit_prediction': start_est,
                        'last_updated': datetime.now()
                    })
                else:
                    predictions.append({
                        'student': student,
                        'rit_prediction': None,
                        'last_updated': datetime.now()
                    })

        return predictions
