# Product overview

**Project topic: website "TechBlog" (review of new tech devices) ** 
  
  Approximate description of the functionality:
	The website is intended for users who want to be the first to learn about new tech devices: smartphones, laptops, tablets, etc.
	The user will be able to read a brief description of the functionality, main characteristics of the device, see photos, and get  a feedback about the product.
	The site will provide the possibility of registration. A registered user will have their own profile page and will be able to write their own posts of review. 			Communication between users is also important. Therefore, the user will be able to rate (like/dislike) the review and write a comment on it.
## URL to website:
https://blog-technological-innovations.herokuapp.com/
## Stack technologies: flask, python, html, css, sqlite, bootstrap.

* Trello - https://trello.com/b/zvIob6WD/blog-an-overview-of-new-tech-products
* Roadmap - https://drive.google.com/file/d/1OBWLyoox4YvS2Rc_xrFGwUw-fkbWV745/view?usp=sharing
* Estimates - https://docs.google.com/spreadsheets/d/1b2Ev-5K4YolZTeYkVMPcZzPE_FU_9bCz62ri6uFccoI/edit?usp=sharing
* CI server -  https://app.circleci.com/pipelines/github/dima-yurchuk/blog_technological_innovations
* Architecture diagram -  https://drive.google.com/file/d/137Cw_mAKtq2IZ_AVsyWadZNN4FSjOYEO/view?usp=sharing
* ER-diagram -  https://drive.google.com/file/d/1bN7CuCRblA6oAfSTkFle_BEPFeQRkJja/view

## Code styling:
Write Python code based on PEP-8 recommendations:
https://www.python.org/dev/peps/pep-0008
* the maximum line length - 79 characters
* start string comments with a space
* take strings in single quotes(but if the string contains an apostrophe, use double quotes)
* use 4 spaces for indentation
* surround operators with 1 space
* functions and classes at the top are limited with two blanked lines
* methods at the top are limited with single blanked line
* variable names write in `snake_case`
* class names write in `CapWords`
* names of functions and methods write in `snake_case`
* import custom modules first, then import python modules
* write package imports in a separate line(except for importing modules from packages)
## Branching policy:
We have a main repository with a single master branch. Before doing a new task, developer do fork of a main repository. After completing the task, developer makes a pull-request, and then his commits will be merged with master branch.
## Setup:
```
python3 -m venv env python -m venv env
Unix Bash:  source env/bin/activate          
Windows: env\Scripts\activate.bat
pip install -r requirements.txt
flask run
```
