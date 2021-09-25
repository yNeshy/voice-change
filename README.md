# mp3effects

Deepens of increases pitch of mp3 files, totally in memory.
Local storage is unnecessary

#### The script works like this:

1. you input the url of the mp3 file you want to work on
2. It edits it automatically
3. It submits it to the S3 bucket of your choice (please know that I have not been able to test the submission to S3 part, if it failed please contact me)


I have also added another type of voice change. I can guide you as to how to use it. (basically I used to decrease the pitch, and I added a high pitched version of the voice change).I have also added another type of voice change. I can guide you as to how to use it. (basically I used to decrease the pitch, and I added a high pitched version of the voice change).
 
by the way, h
### Controlling deepening level
How much the voice changes is controlled by the factor you pass on to these two functions

 
it is called like this :

 10:51 PM
deepen( factor=0.8 )

 
(the factor is expected to be a real between 0 and 1, 0 meaning the voice will be deepened infinitely (or pitched to infinty) and one meaning it won't change )

 
By experimenting, I have set the default value to 0.85 (85%)

 10:55 PM
(for scale, the previous voice change was a factor of 90% )

