# [next version - 1.0] - [TBA]

## version - 0.8 [Improvements to the below] - 22 August 2020 :white_check_mark:
          [known problems]
          [1] When a custom field is renamed, the UI reflects the change, the REST API
          changelog history retains the old name. BUG check ->  "Issues"
          
          [New Feature]
          [1] Saved CheckPoint is now available, just in case the script is interrupted,
          the script can resume back from the last checkpoint.
          

## version - 0.6 [Improvements to the below] - 17 July 2020   
          [known problems]
          [1] When a custom field is renamed, the UI reflects the change, the REST API
          changelog history retains the old name. BUG check ->  "Issues"
          
          [Needed Feature]
          [1] Save CheckPoint (old Persistent Connection) -> Useful when network error occurs or
          authentication is disconnected or other reasons
          
          [New Feature]
          [1] Added a Progress bar using tqdm module, so you can see the progress and time taken
          for the script to run.
          [2] Added Threading to each Post request which cuts down the posting by half the time.
          so processing is much faster.
          
## version - 0.4 [Improvements to the below] - 6 May 2020
          [known problems]
          [1] [Select Cascading list field, can't append 
               one values to options method] BUG on Jira check ->  "Issues"
          [2] Persistent Connection -> Useful when network error occurs or
          authentication is disconnected or other reasons

## version - 0.2 [Initial version of scripts]
          [known problems]
          [1] [Select Cascading list field, can't append 
               one values to options method]
          [2] [Fields without Global context can't be
               used]
          [3] [Issue limit is now 100 issues and the
              startAt parameter gets the records at that starting point]
          [4] [It seems special characters can't be posted] - [Yet to be validated]
