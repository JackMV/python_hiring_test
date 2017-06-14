import pandas as pd
import csv
import decimal
"""Main script for generating output.csv."""
def main():
    # add basic program logic here
    #Need to name and order the columns here or else they will end up ordered arbitrarily
    outputData = pd.DataFrame(columns=["SubjectId","Stat","Split","Subject","Value"])
    outputLocation = "./data/processed/output.csv"
    readData = pd.read_csv('./data/raw/pitchdata.csv')
    hitterData = hitters(readData)
    pitcherData = pitchers(readData)
    #iterate through each batter and store their data in the final DataFrame
    for row in hitterData.itertuples():
        split = ""
        subject = ""
        stat = ""
        if row[4] == 'R':
            split = "vs RHP"
        else:
            split = "vs LHP"
        if row[5] < 1000:
            subject = "HitterTeamId"
        else:
            subject = "HitterId"
        subjectId = row[5]
        #get each of the stats and add row to outputData
        for i in range(4):
            if i == 0:
                stat = "AVG"
                data = [{"SubjectId":subjectId,"Stat":stat,"Split":split,"Subject":subject,"Value":row[1]}]
                outputData = outputData.append(data)
            if i == 1:
                stat = "OBP"
                data = [{"SubjectId":subjectId,"Stat":stat,"Split":split,"Subject":subject,"Value":row[2]}]
                outputData = outputData.append(data)
            if i == 2:
                stat = "SLG"
                data = [{"SubjectId":subjectId,"Stat":stat,"Split":split,"Subject":subject,"Value":row[6]}]
                outputData = outputData.append(data)
            if i == 3:
                stat = "OPS"
                data = [{"SubjectId":subjectId,"Stat":stat,"Split":split,"Subject":subject,"Value":row[3]}]
                outputData = outputData.append(data)
    #iterate through each pitcher and store their data to the final DataFrame
    for row in pitcherData.itertuples():
        split = ""
        subject = ""
        stat = ""
        if row[4] == 'R':
            split = "vs RHH"
        else:
            split = "vs LHH"
        if row[5] < 1000:
            subject = "PitcherTeamId"
        else:
            subject = "PitcherId"
        subjectId = row[5]
        #get each of the stats and add row to outputData
        for i in range(4):
            if i == 0:
                stat = "AVG"
                data = [{"SubjectId":subjectId,"Stat":stat,"Split":split,"Subject":subject,"Value":row[1]}]
                outputData = outputData.append(data)
            if i == 1:
                stat = "OBP"
                data = [{"SubjectId":subjectId,"Stat":stat,"Split":split,"Subject":subject,"Value":row[2]}]
                outputData = outputData.append(data)
            if i == 2:
                stat = "SLG"
                data = [{"SubjectId":subjectId,"Stat":stat,"Split":split,"Subject":subject,"Value":row[6]}]
                outputData = outputData.append(data)
            if i == 3:
                stat = "OPS"
                data = [{"SubjectId":subjectId,"Stat":stat,"Split":split,"Subject":subject,"Value":row[3]}]
                outputData = outputData.append(data)
    #sort the DataFrame
    outputData = outputData.sort_values(["SubjectId","Stat","Split","Subject"], ascending=True)
    outputData.to_csv(path_or_buf=outputLocation,index=False)

def pitchers(inputData):
    returnData = pd.DataFrame()
    vsRHH = inputData[inputData['HitterSide'] == 'R']
    vsLHH = inputData[inputData['HitterSide'] == 'L']
    groupedvsR = vsRHH.groupby('PitcherId')['PA','AB','H','2B','3B','HR','TB','BB','SF','HBP'].sum()
    groupedvsL = vsLHH.groupby('PitcherId')['PA','AB','H','2B','3B','HR','TB','BB','SF','HBP'].sum()
    teamvsR = vsRHH.groupby('PitcherTeamId')['PA','AB','H','2B','3B','HR','TB','BB','SF','HBP'].sum()
    teamvsL = vsLHH.groupby('PitcherTeamId')['PA','AB','H','2B','3B','HR','TB','BB','SF','HBP'].sum()
    #get rid of the rows with less than 25 total plate appearances
    pickyGroupedvR = groupedvsR[groupedvsR['PA'] >= 25]
    pickyGroupedvL = groupedvsL[groupedvsL['PA'] >= 25]
    #gets stats for pitcher vs rhh
    for row in pickyGroupedvR.itertuples():
        avg = battingAvg(row)
        obp = onBase(row)
        slg = sluggingAvg(row)
        ops = onPlusSlug(row)
        pitcher = 'R'
        #store the data as a list of one dict to easily append it to the returnData DataFrame
        data = [{'PlayerId' : row[0], 'AVG' : avg, 'OBP' : obp, 'SLG' : slg, 'OPS' : ops, 'Opponent' : pitcher}]
        returnData = returnData.append(data)
    #gets stats for pitcher vs lhh
    for row in pickyGroupedvL.itertuples():
        avg = battingAvg(row)
        obp = onBase(row)
        slg = sluggingAvg(row)
        ops = onPlusSlug(row)
        pitcher = 'L'
        data = [{'PlayerId' : row[0], 'AVG' : avg, 'OBP' : obp, 'SLG' : slg, 'OPS' : ops, 'Opponent' : pitcher}]
        returnData = returnData.append(data)
    #gets stats for team vs rhh
    for team in teamvsR.itertuples():
        avg = battingAvg(team)
        obp = onBase(team)
        slg = sluggingAvg(team)
        ops = onPlusSlug(team)
        pitcher = 'R'
        data = [{'PlayerId' : team[0], 'AVG' : avg, 'OBP' : obp, 'SLG' : slg, 'OPS' : ops, 'Opponent' : pitcher}]
        returnData = returnData.append(data)
    #gets stats for team vs lhh
    for team in teamvsL.itertuples():
        avg = battingAvg(team)
        obp = onBase(team)
        slg = sluggingAvg(team)
        ops = onPlusSlug(team)
        pitcher = 'L'
        data = [{'PlayerId' : team[0], 'AVG' : avg, 'OBP' : obp, 'SLG' : slg, 'OPS' : ops, 'Opponent' : pitcher}]
        returnData = returnData.append(data)
    return returnData

def hitters(inputData):
    returnData = pd.DataFrame()
    #separate data vs righties and lefties
    vsRHP = inputData[inputData['PitcherSide'] == 'R']
    vsLHP = inputData[inputData['PitcherSide'] == 'L']
    #group data for each unique batter into one row
    groupedvsR = vsRHP.groupby('HitterId')['PA','AB','H','2B','3B','HR','TB','BB','SF','HBP'].sum()
    groupedvsL = vsLHP.groupby('HitterId')['PA','AB','H','2B','3B','HR','TB','BB','SF','HBP'].sum()
    #group data for each unique team into one row
    teamvsR = vsRHP.groupby('HitterTeamId')['PA','AB','H','2B','3B','HR','TB','BB','SF','HBP'].sum()
    teamvsL = vsLHP.groupby('HitterTeamId')['PA','AB','H','2B','3B','HR','TB','BB','SF','HBP'].sum()

    #get rid of the rows with less than 25 total plate appearances
    pickyGroupedvR = groupedvsR[groupedvsR['PA'] >= 25]
    pickyGroupedvL = groupedvsL[groupedvsL['PA'] >= 25]
    #gets stats for player vs rhp
    for row in pickyGroupedvR.itertuples():
        avg = battingAvg(row)
        obp = onBase(row)
        slg = sluggingAvg(row)
        ops = onPlusSlug(row)
        pitcher = 'R'
        #store the data as a list of one dict to easily append it to the returnData DataFrame
        data = [{'PlayerId' : row[0], 'AVG' : avg, 'OBP' : obp, 'SLG' : slg, 'OPS' : ops, 'Opponent' : pitcher}]
        returnData = returnData.append(data)
    #gets stats for player vs lhp
    for row in pickyGroupedvL.itertuples():
        avg = battingAvg(row)
        obp = onBase(row)
        slg = sluggingAvg(row)
        ops = onPlusSlug(row)
        pitcher = 'L'
        data = [{'PlayerId' : row[0], 'AVG' : avg, 'OBP' : obp, 'SLG' : slg, 'OPS' : ops, 'Opponent' : pitcher}]
        returnData = returnData.append(data)
    #gets stats for team vs rhp
    for team in teamvsR.itertuples():
        avg = battingAvg(team)
        obp = onBase(team)
        slg = sluggingAvg(team)
        ops = onPlusSlug(team)
        pitcher = 'R'
        data = [{'PlayerId' : team[0], 'AVG' : avg, 'OBP' : obp, 'SLG' : slg, 'OPS' : ops, 'Opponent' : pitcher}]
        returnData = returnData.append(data)
    #gets stats for team vs lhp
    for team in teamvsL.itertuples():
        avg = battingAvg(team)
        obp = onBase(team)
        slg = sluggingAvg(team)
        ops = onPlusSlug(team)
        pitcher = 'L'
        data = [{'PlayerId' : team[0], 'AVG' : avg, 'OBP' : obp, 'SLG' : slg, 'OPS' : ops, 'Opponent' : pitcher}]
        returnData = returnData.append(data)
    return returnData


#calculates the various stats for players
#used the decimal package because I thought I was getting floating point errors
#some of my results varied slightly from the expected results but this didn't seem to help
D = decimal.Decimal
def battingAvg(player):
    return "{:0.3f}".format((D(player[3])/D(player[2]))).rstrip('0').rstrip('.')

def onBase(player):
    return "{:0.3f}".format(((D(player[3]) + D(player[8]) + D(player[10]))/D(player[1]))).rstrip('0').rstrip('.')

def sluggingAvg(player):
    return "{:0.3f}".format((D(player[7])/D(player[2]))).rstrip('0').rstrip('.')

def onPlusSlug(player):
    return "{:0.3f}".format((D(onBase(player))+D(sluggingAvg(player)))).rstrip('0').rstrip('.')



if __name__ == '__main__':
    main()
