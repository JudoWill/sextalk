python_exec    = python
md2reveal_exec = md2reveal.py
title  = "PhillyQS: Sex Talk"
author = "Will Dampier"
target = "SexTalk.md"

args = --html_title $(title) --html_author $(author)

all:
	$(python_exec) $(md2reveal_exec) $(target) --output index.html $(args)
commit:
	@-make push

push:
	make
	git status
	git add Makefile
	git add src
	git add *.md *.py
	git commit -a
	git push

clean:
	find . -name "*~" | xargs -I {} rm {}
	find . -name "\#" | xargs -I {} rm {}
	find . -name "*.pyc" | xargs -I {} rm {}
	rm -fv demo.html
	rm -rfv .render_cache/

#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=
# Build dependencies
#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=

build_deps:
	make build_reveal.js
	git submodule init 
	git submodule update

build_reveal.js:
	-git submodule add https://github.com/hakimel/reveal.js.git reveal.js
