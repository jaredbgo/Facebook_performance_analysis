# Facebook_performance_analysis
Program to visualize and analyze facebook post performance

This program analysis post performance. The three perforformance measures are organic reach, user engagement (total number of likes, comments, and shares), and user clicks (the unique number of individuals who clicked on a link within a post).

The program runs three simple linear regressions to visualize and analyze relationships between these performance variables. 

It also runs levene's test and t-tests for each performance variable for the following paired groups: posts with and without hashtags, posts with videos vs images.

Furthermore, the program runs an ANOVA for the following groups: posts of different number of hashtags, posts of different lengths, post made at three specific times (8:00 AM, 12:00 PM, 8:00 PM). 

All of this data is also summarized in graphs, and is also printed numerically at the end of the program. 

Step 1: Go to https://developers.facebook.com/tools/explorer/ and log in to your facebook account
- Click "Get Token" and be sure to check off "user_managed_groups"(if you want to analyze a group you manage), "user_posts" (if you want to analyze your own page), and "read_insights" (YOU MUST CHECK THIS OFF SO THE PROGRAM RETURNS ANALYTICAL INSIGHT DATA)
- Click "Get Access Token", copy the generated token, and assign it to the variable "access_token" as a string on line 76

Step 2: Go to https://findmyfbid.com/, copy the url of the facebook page you are hoping to analyze, copy and paste on line 78 to assign to the variable "facebook_user_id"

Step 3: Run the code once to get levene's test p-values for the independent samples t-tests. These will be printed at the end of the program, organized by specific groups and outcome variable being tested 
- Change the "equal_var" arguments on lines 247, 279, 310, 794, 798, 802, 893, 918, and 961 based on the resulting levene's test p-values (p <= .05: equal_var = False, p > .05: equal_var = True)

After adjusting the t-tests, run the code one last time to extract the insights. 
