import requests_oauthlib
import webbrowser
import json
import pickle
import pprint
import requests
import unittest
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
reload(sys)
sys.setdefaultencoding('utf-8')

#Post dictionary that gets data for indivual posts
class Post():
    def __init__(self, post_dict={}):
        if 'message' in post_dict:
            self.message = post_dict['message'] #extracts the message of each post
        else:
            self.message = ""
        self.user = post_dict["from"]["name"] #who posted it?
        self.timeposted = post_dict["created_time"].split("T")[1][0:8] #when was it created?
        if "comments" in post_dict:
            self.commentcount = len(post_dict["comments"]["data"])
            commentlist = []
            for each in post_dict["comments"]["data"]:
                commentlist.append(each["message"])
            self.commentlist = commentlist
        else:
            self.commentcount = 0
            self.commentlist = []

        if "likes" in post_dict:
            self.likecount = len(post_dict["likes"]["data"])
        else:
            self.likecount = 0
        if "shares" in post_dict:
            self.sharecount = int(post_dict["shares"]["count"])
        else:
            self.sharecount = 0
        self.organicreach = post_dict["insights"]["data"][8]["values"][0]["value"]
        self.organicimpressions = post_dict["insights"]["data"][9]["values"][0]["value"]
        if post_dict["insights"]["data"][20]["values"][0]["value"] == 0:
            self.isvideo = False
        else:
            self.isvideo = True
        self.engagementscore = self.likecount + self.commentcount + self.sharecount
        if "#" in self.message:
            hashtag_count = 0
            for char in self.message:
                if char == "#":
                    hashtag_count += 1
            self.hashtag_count = hashtag_count
        else:
            self.hashtag_count = 0
#        self.userclicks = post_dict["insights"]["data"][-15]["values"][0]["value"]
        if "link clicks" in post_dict["insights"]["data"][47]["values"][0]["value"].keys():
            self.userclicks = post_dict["insights"]["data"][47]["values"][0]["value"]["link clicks"]
        else:
            self.userclicks = 0
        self.reachfromlike = post_dict["insights"]["data"][14]["values"][0]["value"]
        self.paidreach = post_dict["insights"]["data"][6]["values"][0]["value"]
        self.totalreach = post_dict["insights"]["data"][4]["values"][0]["value"]


#confidence interval function

def confidence_int(list):
    mean = np.average(list)
    CI = 1.96 * stats.sem(list)
    return (mean-CI, mean+CI)

#***** ACCESSING DATA *****

access_token = "" #enter access token here

facebook_user_ID = #enter user ID here


FB_url = "https://graph.facebook.com/v2.3/{}/posts".format(facebook_user_ID)


url_params = {}
url_params["access_token"] = access_token
url_params["fields"] = "message,created_time,from,comments{like_count,from,message,created_time}, likes, shares, insights" # Parameter key-value so you can get post message, comments, likes, etc. as described in assignment instructions.
url_params["limit"] = 100



raw_FB_data = requests.get(FB_url, url_params)

json_FB_data = json.loads(raw_FB_data.text)


FB_json_list = json_FB_data["data"]
facebook_instance_list = [] #this is creating a list of post instances
for each in FB_json_list: #turning each dictionary into a post instance
    facebook_instance_list.append(Post(each)) # creating list of instances

#SUMMARY DATA
summary_data = {}
reachlist = [each.organicreach for each in facebook_instance_list]
engagelist = [each.engagementscore for each in facebook_instance_list]
clickslist = [each.userclicks for each in facebook_instance_list]

summary_data["N"] = [len(reachlist), len(engagelist), len(clickslist)]
summary_data["mean"] = [np.average(reachlist), np.average(engagelist), np.average(clickslist)]
summary_data["sd"]= [np.std(reachlist), np.std(engagelist), np.std(clickslist)]
summary_data["max"] = [np.amax(reachlist), np.amax(engagelist), np.amax(clickslist)]
summary_data["min"] = [np.amin(reachlist), np.amin(engagelist), np.amin(clickslist)]
summary_data["median"] = [np.median(reachlist), np.median(engagelist), np.median(clickslist)]



# ***** MAKING PLOTS OF THE DATA *****

regression_data = []
regression_data.append(("Name", "p-value", "r-squared"))
ttest_data = []
ttest_data.append(("Name", "confidence intervals", "p-value"))

plot_data = []
for each in facebook_instance_list:
        plot_data.append((each.engagementscore,each.organicreach))
x = []
y = []
for each in plot_data:
    x.append(each[0])
    y.append(each[1])

plt.plot(x,y,"o")

# ***** TRENDLINE *****

z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"r--")

plt.title("User Engagement vs. Organic Reach")
plt.xlabel("# of Post Likes, Comments, and Shares")
plt.ylabel("Organic Reach (Unique Users)")
plt.show()
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
regression_data.append(("Engagement vs. Total Lifetime Organic Reach", p_value, r_value*r_value))

#engagement vs user clicks


plot_data = []
for each in facebook_instance_list:
        plot_data.append((each.engagementscore,each.userclicks))
x = []
y = []
for each in plot_data:
    x.append(each[0])
    y.append(each[1])

plt.plot(x,y,"o")


z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"r--")

plt.title("User Engagement vs. Number of Unique Users who Clicked Post")
plt.xlabel("# of Post Likes, Comments, and Shares")
plt.ylabel("# of Unique Users who Clicked Post")
plt.show()
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
regression_data.append(("Engagement vs. User clicks", p_value, r_value*r_value))


#Organic reach vs user clicks


plot_data = []
for each in facebook_instance_list:
#    if each.engagementscore < 50: #to reduct outliers
        plot_data.append((each.organicreach,each.userclicks))
x = []
y = []
for each in plot_data:
    x.append(each[0])
    y.append(each[1])

plt.plot(x,y,"o")


z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"r--")

plt.title("Organic Reach vs. Number of Unique Users who Clicked Post")
plt.xlabel("Organic Reach (Unique Users)")
plt.ylabel("# of Unique Users who Clicked Post")
plt.show()
slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
regression_data.append(("Organic reach vs. User clicks", p_value, r_value*r_value))


#WORKING WITH HASHTAG COUNTS



#Hash vs non hash
hashsummary = []
hashsummary.append(["Averages", "levene", "p-val"])
hash_list = []
nonhash_list =[]
for each in facebook_instance_list:
    if each.hashtag_count != 0:
        hash_list.append([each.organicreach, each.engagementscore, each.userclicks])
    else:
        nonhash_list.append([each.organicreach, each.engagementscore, each.userclicks])

hash_dict = {}
hash_dict["Posts With Hashtags"] = hash_list
hash_dict["Posts Without Hashtags"]= nonhash_list
hash_org_reach = {}
for each in hash_dict.keys():
    list = []
    for post in hash_dict[each]:
        list.append(post[0])
    hash_org_reach[each] = np.average(list)


plt.bar(range(len(hash_org_reach)), hash_org_reach.values(), align='center', width = .7,color = "r")
plt.xticks(range(len(hash_org_reach)), hash_org_reach.keys())
plt.ylabel("Average Organic Reach (Unique Users)")

plt.title("Average Organic Reach for Posts With and Without Hashtags")
plt.show()


hash_org = [each[0] for each in hash_list]
non_hash_org = [each[0] for each in nonhash_list]

labels = ["", "Posts Without Hashtags", "Posts With Hashtags"]
plt.boxplot([non_hash_org, hash_org])
plt.ylabel("Organic Reach (Unique Users)")

plt.xticks(np.arange(len(labels)), labels)
plt.title("Organic Reach for Posts With and Without Hashtags")
plt.show()

poop1, hashp = stats.ttest_ind(non_hash_org, hash_org, equal_var=True)
W1, leev = stats.levene(non_hash_org, hash_org)
hashsummary.append([hash_org_reach, leev, hashp])


hash_engagement = {}
for each in hash_dict.keys():
    list = []
    for post in hash_dict[each]:
        list.append(post[1])
    hash_engagement[each] = np.average(list)


plt.bar(range(len(hash_engagement)), hash_engagement.values(), align='center', width = .7,color = "r")
plt.xticks(range(len(hash_engagement)), hash_engagement.keys())
plt.ylabel("Average # of Likes, Comments, and Shares")

plt.title("Average User Engagement for Posts With and Without Hashtags")
plt.show()


hash_eng = [each[1] for each in hash_list]
non_hash_eng= [each[1] for each in nonhash_list]

labels = ["", "Posts Without Hashtags", "Posts With Hashtags"]
plt.boxplot([non_hash_eng, hash_eng])
plt.ylabel("# of Likes, Comments, and Shares")

plt.xticks(np.arange(len(labels)), labels)
plt.title("User Engagement for Posts With and Without Hashtags")
plt.show()

poop1, hashp = stats.ttest_ind(non_hash_eng, hash_eng, equal_var=True)
W1, leev = stats.levene(non_hash_eng, hash_eng)
hashsummary.append([hash_engagement, leev, hashp])

hash_clicks = {}
for each in hash_dict.keys():
    list = []
    for post in hash_dict[each]:
        list.append(post[2])
    hash_clicks[each] = np.average(list)


plt.bar(range(len(hash_clicks)), hash_clicks.values(), align='center', width = .7,color = "r")
plt.xticks(range(len(hash_clicks)), hash_clicks.keys())
plt.ylabel("Average # Unique Users who Clicked Post")

plt.title("Average Number of Unique Users who Clicked Posts With and Without Hashtags")
plt.show()


hash_clix = [each[2] for each in hash_list]
non_hash_clix= [each[2] for each in nonhash_list]

labels = ["", "Posts Without Hashtags", "Posts With Hashtags"]
plt.boxplot([non_hash_clix, hash_clix])
plt.ylabel("# of Unique Users who Clicked Post")

plt.xticks(np.arange(len(labels)), labels)
plt.title("Unique Users Who Clicked Posts With and Without Hashtags")
plt.show()

poop1, hashp = stats.ttest_ind(non_hash_clix, hash_clix, equal_var=True)
W1, leev = stats.levene(non_hash_clix, hash_clix)
hashsummary.append([hash_clicks, leev, hashp])

#By hash number
hash1 = []
hash2 = []
hash3 = []
hash4 = []
hash5 = []
hash6 = []
for each in facebook_instance_list:
    if each.hashtag_count == 1:
        hash1.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.hashtag_count == 2:
        hash2.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.hashtag_count == 3:
        hash3.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.hashtag_count == 4:
        hash4.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.hashtag_count == 5:
        hash5.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.hashtag_count > 5:
        hash6.append([each.organicreach, each.engagementscore, each.userclicks])

hashtag_dict = {}
hashtag_dict[1] = hash1
hashtag_dict[2] = hash2
hashtag_dict[3] = hash3
hashtag_dict[4] = hash4
hashtag_dict[5] = hash5
hashtag_dict["6+"] = hash6
hashtagsample = [len(hash1), len(hash2), len(hash3), len(hash4), len(hash5), len(hash6)]


#hashtag count versus reach

hashtag_reach = {}
for each in hashtag_dict.keys():
    list = []
    for post in hashtag_dict[each]:
        list.append(post[0])
    hashtag_reach[each] = np.average(list)
plt.bar(range(len(hashtag_reach)), hashtag_reach.values(), align='center', width = .3,color = "r")
plt.xticks(range(len(hashtag_reach)), hashtag_reach.keys())
plt.ylabel("Average Organic Reach (Unique Users)")
plt.xlabel("# of Hashtags in Post")
plt.title("Average Organic Reach for Posts with Hashtags")



plt.show()

labels = ["", "1", "2", "3", "4", "5", "6+"]
hash1reach = [each[0] for each in hash1]
hash2reach = [each[0] for each in hash2]
hash3reach = [each[0] for each in hash3]
hash4reach = [each[0] for each in hash4]
hash5reach = [each[0] for each in hash5]
hash6reach = [each[0] for each in hash6]



plt.boxplot([hash1reach, hash2reach, hash3reach, hash4reach, hash5reach, hash6reach])
plt.ylabel("Organic Reach (Unique Users)")
plt.xlabel("# of Hashtags in Post")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Organic Reach for Posts with Hashtags")
plt.show()

#hash count verses engagement

hashtag_engagement = {}
for each in hashtag_dict.keys():
    list = []
    for post in hashtag_dict[each]:
        list.append(post[1])
    hashtag_engagement[each] = np.average(list)
plt.bar(range(len(hashtag_engagement)), hashtag_engagement.values(), align='center', width = .3,color = "r")
plt.xticks(range(len(hashtag_engagement)), hashtag_engagement.keys())
plt.ylabel("Average # of Post Likes, Comments, and Shares")
plt.xlabel("# of Hashtags in Post")
plt.title("Average User Engagement for Posts with Hashtags")
plt.show()


hash1eng = [each[1] for each in hash1]
hash2eng = [each[1] for each in hash2]
hash3eng = [each[1] for each in hash3]
hash4eng = [each[1] for each in hash4]
hash5eng = [each[1] for each in hash5]
hash6eng = [each[1] for each in hash6]



plt.boxplot([hash1eng, hash2eng, hash3eng, hash4eng, hash5eng, hash6eng])
plt.ylabel("# of Post Likes, Comments, and Shares")
plt.xlabel("# of Hashtags in Post")
plt.xticks(np.arange(len(labels)), labels)
plt.title("User Engagement for Posts with Hashtags")
plt.show()

#hash count vs clicks

hashtag_clicks = {}
for each in hashtag_dict.keys():
    list = []
    for post in hashtag_dict[each]:
        list.append(post[2])
    hashtag_clicks[each] = np.average(list)
plt.bar(range(len(hashtag_clicks)), hashtag_clicks.values(), align='center', width = .3,color = "r")
plt.xticks(range(len(hashtag_clicks)), hashtag_clicks.keys())
plt.ylabel("Average # of Unique Users who Clicked Post")
plt.xlabel("# of Hashtags in Post")
plt.title("Average Unique Users who Clicked Posts with Hashtags")

plt.show()


hash1clix = [each[2] for each in hash1]
hash2clix = [each[2] for each in hash2]
hash3clix = [each[2] for each in hash3]
hash4clix = [each[2] for each in hash4]
hash5clix = [each[2] for each in hash5]
hash6clix = [each[2] for each in hash6]



plt.boxplot([hash1clix, hash2clix, hash3clix, hash4clix, hash5clix, hash6clix])
plt.ylabel("# of Unique Users who Clicked")
plt.xlabel("# of Hashtags in Post")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Unique Users who Clicked Posts with Hashtags")
plt.show()


#POST LENGTH

len1 = []
len2 = []
len3 = []
len4 = []
len5 = []
for each in facebook_instance_list:
    if len(each.message.split()) <= 20:
        len1.append([each.organicreach, each.engagementscore, each.userclicks])
    elif len(each.message.split()) <=40:
        len2.append([each.organicreach, each.engagementscore, each.userclicks])
    elif len(each.message.split()) <= 60:
        len3.append([each.organicreach, each.engagementscore, each.userclicks])
    elif len(each.message.split()) <= 80:
        len4.append([each.organicreach, each.engagementscore, each.userclicks])
    else:
        len5.append([each.organicreach, each.engagementscore, each.userclicks])
len_dict = {}
len_dict["0-20"] = len1 #0-20
len_dict["20-40"] = len2 #20-40
len_dict["40-60"] = len3
len_dict["60-80"] = len4
len_dict["80+"] = len5 #over 80

lengthsample = [len(len1), len(len2), len(len3), len(len4), len(len5)]


#length vs organic reach
len_reach = {}
for each in len_dict.keys():
    list = []
    for post in len_dict[each]:
        list.append(post[0])
    len_reach[each] = np.average(list)
len_reach_items = sorted(len_reach.items(), key = lambda x: int(x[0][0]))
xbar = []
ybar = []
for each in len_reach_items:
    xbar.append(each[0])
    ybar.append(each[1])

plt.bar(np.arange(len(xbar)), ybar, align = "center", width = .3, color = "r")
plt.xticks(np.arange(len(xbar)), xbar)

plt.ylabel("Average Organic Reach (Unique Users)")
plt.xlabel("Length of Post (Words)")
plt.title("Average Organic Reach for Posts of Different Lengths")

plt.show()

labels = ["", "0-20", "20-40", "40-60", "60-80", "80+"]

len1reach = [each[0] for each in len1]
len2reach = [each[0] for each in len2]
len3reach = [each[0] for each in len3]
len4reach = [each[0] for each in len4]
len5reach = [each[0] for each in len5]




plt.boxplot([len1reach, len2reach, len3reach, len4reach, len5reach])
plt.ylabel("Organic Reach (Unique Users)")
plt.xlabel("Length of Post (Words)")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Organic Reach for Posts of Different Lengths")
plt.show()


#length vs engagement

len_engagement = {}
for each in len_dict.keys():
    list = []
    for post in len_dict[each]:
        list.append(post[1])
    len_engagement[each] = np.average(list)

len_engagement_items = sorted(len_engagement.items(), key = lambda x: int(x[0][0]))
xbar = []
ybar = []
for each in len_engagement_items:
    xbar.append(each[0])
    ybar.append(each[1])

plt.bar(np.arange(len(xbar)), ybar, align = "center", width = .3, color = "r")
plt.xticks(np.arange(len(xbar)), xbar)


plt.ylabel("Average # of Post Likes, Comments, and Shares")
plt.xlabel("Length of Post (Words)")
plt.title("Average User Engagement for Posts of Different Lengths")

plt.show()



len1eng = [each[1] for each in len1]
len2eng = [each[1] for each in len2]
len3eng = [each[1] for each in len3]
len4eng = [each[1] for each in len4]
len5eng = [each[1] for each in len5]




plt.boxplot([len1eng, len2eng, len3eng, len4eng, len5eng])
plt.ylabel("# of Post Likes, Comments, and Shares")
plt.xlabel("Length of Post (Words)")
plt.xticks(np.arange(len(labels)), labels)
plt.title("User Engagement for Posts of Different Lengths")
plt.show()

#length vs. clicks

len_clicks = {}
for each in len_dict.keys():
    list = []
    for post in len_dict[each]:
        list.append(post[2])
    len_clicks[each] = np.average(list)

len_clicks_items = sorted(len_clicks.items(), key = lambda x: int(x[0][0]))
xbar = []
ybar = []
for each in len_clicks_items:
    xbar.append(each[0])
    ybar.append(each[1])

plt.bar(np.arange(len(xbar)), ybar, align = "center", width = .3, color = "r")
plt.xticks(np.arange(len(xbar)), xbar)


plt.ylabel("Average # of Unique Users who Clicked Post")
plt.xlabel("Length of Post (Words)")
plt.title("Average Unique Users who Clicked Posts of Different Lengths")

plt.show()


len1clix = [each[2] for each in len1]
len2clix = [each[2] for each in len2]
len3clix = [each[2] for each in len3]
len4clix = [each[2] for each in len4]
len5clix = [each[2] for each in len5]



plt.boxplot([len1clix, len2clix, len3clix, len4clix, len5clix])
plt.ylabel("# of Unique Users who Clicked Post")
plt.xlabel("Length of Post (Words)")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Unique Users who Clicked Posts of Different Lengths")
plt.show()

reaching = [len1reach, len2reach, len3reach, len4reach, len5reach]
engaging = [len1eng, len2eng, len3eng, len4eng, len5eng]
clicking = [len1clix, len2clix, len3clix, len4clix, len5clix]

length_anova = []
leedle, myp = stats.f_oneway(len1reach, len2reach, len3reach, len4reach, len5reach)
length_anova.append(myp)
leedle, myp = stats.f_oneway(len1eng, len2eng, len3eng, len4eng, len5eng)
length_anova.append(myp)
leedle, myp = stats.f_oneway(len1clix, len2clix, len3clix, len4clix, len5clix)
length_anova.append(myp)


#WORKING WITH TIMING



time8A = []
time12 = []
time8P = []

for each in facebook_instance_list:
    if each.timeposted[0:5] == "07:00":
        time8A.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.timeposted[0:5] == "11:00":
        time12.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.timeposted[0:5] == "19:00":
        time8P.append([each.organicreach, each.engagementscore, each.userclicks])
time1_dict = {}
time1_dict["8:00 AM1"] = time8A
time1_dict["12:00 PM2"] = time12
time1_dict["8:00 PM3"] = time8P

timesample = [len(time8A), len(time12), len(time8P)]

#ANOVA
anova_results = {}
fval, ap = stats.f_oneway([each[0] for each in time8A], [each[0] for each in time12], [each[0] for each in time8P])
anova_results["timing reach"] = ap
fval, ap = stats.f_oneway([each[1] for each in time8A], [each[1] for each in time12], [each[1] for each in time8P])
anova_results["timing engagement"] = ap
fval, ap = stats.f_oneway([each[2] for each in time8A], [each[2] for each in time12], [each[2] for each in time8P])
anova_results["timing clicks"] = ap
#time1 vs organic reach
time1_reach = {}
for each in time1_dict.keys():
    list = []
    for post in time1_dict[each]:
        list.append(post[0])
    time1_reach[each] = np.average(list)

time1_reach_items = sorted(time1_reach.items(), key = lambda x: int(x[0][-1]))
xbar = []
ybar = []

for each in time1_reach_items:
    xbar.append(each[0][:-1])
    ybar.append(each[1])

plt.bar(np.arange(len(xbar)), ybar, align = "center", width = .3, color = "r")
plt.xticks(np.arange(len(xbar)), xbar)

plt.ylabel("Average Organic Reach (Unique Users)")
plt.xlabel("Time Posted")
plt.title("Average Organic Reach for Posts Created at Different Times")

plt.show()

time1reach = [each[0] for each in time8A]
time2reach = [each[0] for each in time12]
time3reach = [each[0] for each in time8P]

labels = ["", "8:00 AM", "12:00 PM", "8:00 PM"]

plt.boxplot([time1reach, time2reach, time3reach])
plt.ylabel("Organic Reach (Unique Users)")
plt.xlabel("Time Posted")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Organic Reach for Posts Created at Different Times")
plt.show()

#time1 vs engagement

time1_engage = {}
for each in time1_dict.keys():
    list = []
    for post in time1_dict[each]:
        list.append(post[1])
    time1_engage[each] = np.average(list)
time1_engage_items = sorted(time1_engage.items(), key = lambda x: int(x[0][-1]))
xbar = []
ybar = []

for each in time1_engage_items:
    xbar.append(each[0][:-1])
    ybar.append(each[1])

plt.bar(np.arange(len(xbar)), ybar, align = "center", width = .3, color = "r")
plt.xticks(np.arange(len(xbar)), xbar)

plt.ylabel("Average # of Post Likes, Comments, and Shares")
plt.xlabel("Time Posted")
plt.title("Average User Engagement for Posts Created at Different Times")

plt.show()

time1eng = [each[1] for each in time8A]
time2eng = [each[1] for each in time12]
time3eng = [each[1] for each in time8P]

labels = ["", "8:00 AM", "12:00 PM", "8:00 PM"]

plt.boxplot([time1eng, time2eng, time3eng])
plt.ylabel("# of Post Likes, Comments, and Shares")
plt.xlabel("Time Posted")
plt.xticks(np.arange(len(labels)), labels)
plt.title("User Engagement for Posts Created at Different Times")
plt.show()

#time1 vs clicks

time1_clicks = {}
for each in time1_dict.keys():
    list = []
    for post in time1_dict[each]:
        list.append(post[2])
    time1_clicks[each] = np.average(list)

time1_clicks_items = sorted(time1_clicks.items(), key = lambda x: int(x[0][-1]))
xbar = []
ybar = []

for each in time1_clicks_items:
    xbar.append(each[0][:-1])
    ybar.append(each[1])

plt.bar(np.arange(len(xbar)), ybar, align = "center", width = .3, color = "r")
plt.xticks(np.arange(len(xbar)), xbar)


plt.ylabel("Average # of Unique Users who Clicked Post")
plt.xlabel("Time Posted")
plt.title("Average Unique Users who Clicked Posts Created at Different Times")

plt.show()

time1clix = [each[2] for each in time8A]
time2clix = [each[2] for each in time12]
time3clix = [each[2] for each in time8P]

labels = ["", "8:00 AM", "12:00 PM", "8:00 PM"]

plt.boxplot([time1clix, time2clix, time3clix])
plt.ylabel("# of Unique Users who Clicked Post")
plt.xlabel("Time Posted")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Unique Users who Clicked Posts Created at Different Times")
plt.show()


#Looking at posts at best times vs other posts
best_times = []
other_times = []
for each in facebook_instance_list:
    if each.timeposted[0:5] == "07:00" and each.isvideo == False:
        best_times.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.timeposted[0:5] == "11:00" and each.isvideo == False:
        best_times.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.timeposted[0:5] == "19:00" and each.isvideo == False:
        best_times.append([each.organicreach, each.engagementscore, each.userclicks])
    elif each.isvideo is False:
        other_times.append([each.organicreach, each.engagementscore, each.userclicks])
best_org_list = []
best_engage_list = []
best_userclicks_list = []
other_org_list = []
other_engage_list = []
other_userclicks_list = []
for each in best_times:
    best_org_list.append(each[0])
    best_engage_list.append(each[1])
    best_userclicks_list.append(each[2])
for each in other_times:
    other_org_list.append(each[0])
    other_engage_list.append(each[1])
    other_userclicks_list.append(each[2])


timing_analyses = []
timing_analyses.append(["name", "levene's test", "p-value"])

idc, lv = stats.levene(best_org_list, other_org_list)
dc, apval = stats.ttest_ind(best_org_list,other_org_list, equal_var=True)
timing_analyses.append(("Average organic reach for optimized and non-optimized time posted", lv, apval))

idc, lv = stats.levene(best_engage_list, other_engage_list)
dc, apval = stats.ttest_ind(best_engage_list,other_engage_list, equal_var=True)
timing_analyses.append(("Average engagement score for optimized and non-optimized time posted", lv, apval))
                       
idc, lv = stats.levene(best_userclicks_list, other_userclicks_list)
dc, apval = stats.ttest_ind(best_userclicks_list,other_userclicks_list, equal_var=True)
timing_analyses.append(("Average userclicks for optimized and non-optimized time posted", lv, apval))

org_dict = {}
org_dict["Optimized Posting Time"] = np.average(best_org_list)
org_dict["Non-optimized Posting Time"] = np.average(other_org_list)

plt.bar(range(len(org_dict)), org_dict.values(), align='center', width = .7,color = "r")
plt.xticks(range(len(org_dict)), org_dict.keys())

plt.ylabel("Average Organic Reach (Unique Users)")
plt.title("Average Organic Reach for Posts Made At Optimized and Non-Optimized Times")
plt.show()



labels = ["","Non-optimized Posting Time", "Optimized Posting Time"]

plt.boxplot([other_org_list, best_org_list])
plt.ylabel("Organic Reach (Unique Users)")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Organic Reach for Posts Made At Optimized and Non-Optimized Times")
plt.show()

engage_dict = {}
engage_dict["Optimized Posting Time"] = np.average(best_engage_list)
engage_dict["Non-optimized Posting Time"] = np.average(other_engage_list)

plt.bar(range(len(engage_dict)), engage_dict.values(), align='center', width = .7,color = "r")
plt.xticks(range(len(engage_dict)), engage_dict.keys())

plt.ylabel("Average # of Post Likes, Comments, and Shares")
plt.title("Average User Engagement for Posts Made At Optimized and Non-Optimized Times")
plt.show()

plt.boxplot([other_engage_list, best_engage_list])
plt.ylabel("# of Post Likes, Comments, and Shares")
plt.xticks(np.arange(len(labels)), labels)
plt.title("User Engagement for Posts Made At Optimized and Non-Optimized Times")
plt.show()



userclicks_dict = {}
userclicks_dict["Optimized Posting Time"] = np.average(best_userclicks_list)
userclicks_dict["Non-optimized Posting Time"] = np.average(other_userclicks_list)

plt.bar(range(len(userclicks_dict)), userclicks_dict.values(), align='center', width = .7,color = "r")
plt.xticks(range(len(userclicks_dict)), userclicks_dict.keys())

plt.ylabel("Average # of Unique Users who Clicked Post")
plt.title("Average Unique Users who Clicked Posts Made At Optimized and Non-Optimized Times")
plt.show()


plt.boxplot([other_userclicks_list, best_userclicks_list])
plt.ylabel("# of Unique Users who Clicked Post")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Unique Users who Clicked Posts Made At Optimized and Non-Optimized Times")
plt.show()

#Average organic reach for video vs non video

videoreach = []
nonvideoreach = []
for each in facebook_instance_list:
    if each.isvideo == True:
        videoreach.append(each.organicreach)
    else:
        nonvideoreach.append(each.organicreach)


videodict = {}
videodict["Video Posts"] = np.average(videoreach)
videodict["Image Posts"] = np.average(nonvideoreach)

plt.bar(range(len(videodict)), videodict.values(), align='center', width = .7,color = "r")
plt.xticks(range(len(videodict)), videodict.keys())
plt.ylabel("Average Organic Reach (Unique Users)")
plt.title("Average Organic Reach for Posts with Videos and Images")


plt.show()

labels = ["", "Image Posts", "Video Posts"]
plt.boxplot([nonvideoreach, videoreach])
plt.ylabel("Organic Reach (Unique Users)")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Organic Reach for Posts with Videos and Images")
plt.show()

t1, vidreachp = stats.ttest_ind(videoreach,nonvideoreach, equal_var=True)
ttest_data.append(("Average organic reach for video vs non video", [confidence_int(videoreach), confidence_int(nonvideoreach)], vidreachp))
W1, levenep1 = stats.levene(videoreach, nonvideoreach)


#average engagement for video vs non video

videoengagement = []
nonvideoengagament = []
for each in facebook_instance_list:
    if each.isvideo == True:
        videoengagement.append(each.engagementscore)
    else:
        nonvideoengagament.append(each.engagementscore)


videoengagementdict = {}
videoengagementdict["Video Posts"] = np.average(videoengagement)
videoengagementdict["Image Posts"] = np.average(nonvideoengagament)

plt.bar(range(len(videoengagementdict)), videoengagementdict.values(), align='center', width = .7, color = "r")
plt.xticks(range(len(videoengagementdict)), videoengagementdict.keys())
plt.ylabel("Average # of Post Likes, Comments, and Shares")
plt.title("Average User Engagement for Posts with Videos and Images")

t2, videngagementp = stats.ttest_ind(videoengagement, nonvideoengagament, equal_var=True)
ttest_data.append(("average engagement for video vs non video", [confidence_int(videoengagement), confidence_int(nonvideoengagament)], videngagementp))

W2, levenep2 = stats.levene(videoengagement, nonvideoengagament)


plt.show()

plt.boxplot([nonvideoengagament, videoengagement])
plt.ylabel("# of Post Likes, Comments, and Shares")
plt.xticks(np.arange(len(labels)), labels)
plt.title("User Engagement for Posts with Videos and Images")
plt.show()

#average clicks for video vs non video

videoclicks = []
nonvideoclicks = []
for each in facebook_instance_list:
    if each.isvideo == True:
        videoclicks.append(each.userclicks)
    else:
        nonvideoclicks.append(each.userclicks)


videoclicksdict = {}
videoclicksdict["Video Posts"] = np.average(videoclicks)
videoclicksdict["Image Posts"] = np.average(nonvideoclicks)

plt.bar(range(len(videoclicksdict)), videoclicksdict.values(), align='center', width = .7, color = "r")
plt.xticks(range(len(videoclicksdict)), videoclicksdict.keys())
plt.ylabel("Average # of Unique Users who Clicked Post")
plt.title("Average Number of Unique Users who Clicked Posts with Videos and Images")

plt.show()

plt.boxplot([nonvideoclicks, videoclicks])
plt.ylabel("# of Unique Users who Clicked Post")
plt.xticks(np.arange(len(labels)), labels)
plt.title("Number of Unique Users who Clicked Posts with Videos and Images")
plt.show()


t3, videoclicksp = stats.ttest_ind(videoclicks, nonvideoclicks, equal_var=True)
ttest_data.append(("average user clicks for video vs non video", [confidence_int(videoclicks), confidence_int(nonvideoclicks)], videoclicksp))

W3, levenep3 = stats.levene(videoclicks, nonvideoclicks)

#Analyzing reach
total_reach = []
reach_from_likes = []

for each in facebook_instance_list:
    total_reach.append(each.organicreach)
    reach_from_likes.append(each.reachfromlike)

#paid vs unpaid
paidlist = []
unpaidlist = []
for each in facebook_instance_list:
    if each.paidreach != 0:
        paidlist.append([each.totalreach, each.engagementscore, each.userclicks])
    else:
        unpaidlist.append([each.totalreach, each.engagementscore, each.userclicks])
paidtotreach = [each[0] for each in paidlist]
paidengagement = [each[1] for each in paidlist]
paidclicks = [each[2] for each in paidlist]

unpaidtotreach = [each[0] for each in unpaidlist]
unpaidengagement = [each[1] for each in unpaidlist]
unpaidclicks = [each[2] for each in unpaidlist]


print "SUMMARY"
print summary_data
print ""
print "__REGRESSION DATA__"
print regression_data
print " "
print "__HASH VS. NON-HASH__"
print "total number of hash posts is {}, total number of non hash posts is {}".format(np.sum(hashtagsample), len(FB_json_list) - np.sum(hashtagsample))
print hashsummary
print ""
print "__BAR-CHART DATA___"
print "*** Hashtag Data based on this many posts (ordered by hashtag): {}, and total {}".format(hashtagsample, np.sum(hashtagsample))
print "hashtag_reach is "
print hashtag_reach
print "hashtag engagement is"
print hashtag_engagement
print "hashtag click data is "
print hashtag_clicks
print "***Length Data based on this many posts (ordered by length): {}, and total {}".format(lengthsample, np.sum(lengthsample))
print "len reach data is"
print len_reach
print "len engagement data is"
print len_engagement
print "len click data is"
print len_clicks
print ""
print "__T-TEST DATA for Photo vs video ___"
print "sample based on {} video posts and {} photo post".format(len(videoengagement), len(nonvideoengagament))
print "Levene's p-value for video reach is {}".format(levenep1)
print "Levene's p-value for video engagement is {}".format(levenep2)
print "Levene's p-value for video clicks is {}".format(levenep3)
print ttest_data
print "average video reach is {} and non video reach is {}".format(np.average(videoreach), np.average(nonvideoreach))
print "average video engagement is {} and non video engagement is {}".format(np.average(videoengagement), np.average(nonvideoengagament))

print ""
print "__TIME OPTIMIZATION DATA___"
print "Sample of best times based on (earliest to latest) {} and total is {} ".format(timesample, np.sum(timesample))
print "For posts at best times: average reach is {}, average engagement is {}, average user clicks is {}".format(np.average(best_org_list), np.average(best_engage_list), np.average(best_userclicks_list))
print "For posts at other times, average reach is {}, average engagement is {}, average user clicks is {}".format(np.average(other_org_list), np.average(other_engage_list), np.average(other_userclicks_list))
print "ANOVA RESULTS"
print anova_results
print "Length anova"
print length_anova
print ""
print "T-tests for time optimization:"
print timing_analyses
print "Timing analyses tests should be changed on line 670"
print "number of optimized time posts is {}, and number of other times posts is {}".format(len(best_org_list), len(other_org_list))
print ""
print "__OTHER ANALYSIS__"
print "Total average reach is {}, and average reach from people who like our page is {}".format(np.average(total_reach), np.average(reach_from_likes))
print " "
print "paid vs non-paid average stats: total reach {}, engagement {}, clicks {}".format([np.average(paidtotreach), np.average(unpaidtotreach)], [np.average(paidengagement), np.average(unpaidengagement)], [np.average(paidclicks), np.average(unpaidclicks)])
print "data sample for paid and unpaid: {} paid posts, {} unpaid posts".format(len(paidlist), len(unpaidlist))

print ":)"

