**The 2p data is in TIFF stacks, which are straightforward for us to read and convert, but do you have frame time information?**

Scanning was at 4 Hz (4 frames / second). For prototypical pup call presentation circuits, 3 prototypical calls (1 sec. in duration) were played in a pseudorandom order (repetition rate: 0.1 Hz)' --> This converts to 1 pup call every 40 frames (so, 120 frames to go through all three pup calls, then repeat for a total of 8-10 trials). This is similar to the morph pup call data, but 5 morphs were played per circuit (1 morph every 40 frames = 200 frames to cycle through morphs 1-5, then repeat 8-10 trials). For pure tone circuits, there are 9 tones that alternate in a pseudorandom order once every 20 frames (so, 180 frames to go through each of the 9 tones, then repeat for 8-10 trials).

**The behavior data is in CSVs. We can read these, but it would be helpful if you could provide a README describing how to interpret them. In particular, how does this timing relate to the 2p frame times? Is there an offset?**

No behavior testing was performed in conjunction with electrophysiology or two-photon imaging. I can try to write up a readme file, but each .csv is just a single column and each column has a series of times that correspond to the mouse pressing the lever.

**We would need similar information for ABF files. How would we temporally register them with the 2p data?**

Similar to the behavior data, there is no simultaneous registration required for the 2p data and electrophysiology data. These are all separate experiments. As for the timing information, the .abf files have two channels. The first channel is the electrophysiological recording, and the second channel actually shows the pup call so all of the timing information required for the e-phys data is built into the .abf file.  

**We don't see any results for image segmentation, e.g. with suite2p in the figshare. This isn't necessarily a problem, but we'd like to include it if you have it.**

We didn't use suite2p and I don't think this information is readily available.

**We'd also like to include subject-specific information like sex, age, species, and strain if you have it.**

All data labeled 'virgins' are from 6–48-week-old C57BL/6 virgin female mice (Taconic Biosciences; Jackson Laboratory). Any data from 'dams' are from lactating dams (3–5 months old, Taconic Biosciences).
