\* if we go for CNNs

# Procedure for counting & annotating a bee sample image:
1. If the grad student did a count, get that number from them.
2. Give the image/sample a unique name, preferably 'bee-image-<N+1>'
3. 
- In the image, count bees, drawing roughly straight light green lines over the long axis and centered on each bee. If there is a significant part of a bee (1/3-1/2), draw a straight line centered on the bee using light purple. For partial bees, record 2 part segments as 1 (just assume all significant parts of bees are ~1/2 bee). Record this count. Save the annotated image with the same name but '<source image name>_annotated'. 
- For green lines (full bees) try to keep them as straight as possible and make individual lines distinguisable (so we can pick them up w/ opencv)
- If you make a mistake or can't discern a clump, give an estimate for how many bees you should have counted, add that to the total, and record an instance of error margin (like +/- 2 into a list of recorded error margin instances) 
4. Put the file name/id, total count, and total error margin into the spreadsheet on onedrive.