---
title: What is Jekyll? How to use it?
layout: single
post-image: "http://jekyllcn.com/img/logo-2x.png"
description: Jekyll is a static site generator. You give it text written in your favorite
  markup language and it uses layouts to create a static website.
tags:
- jekyll
- blog
- starter's guide
---
Jekyll is a simple, blog-aware, static site generator perfect for personal, project, or organization sites. Think of it like a file-based CMS, without all the complexity. Jekyll takes your content, renders Markdown and Liquid templates, and spits out a complete, static website ready to be served by Apache, Nginx or another web server. Jekyll is the engine behind GitHub Pages, which you can use to host sites right from your GitHub repositories and if you don't know what GitHub Pages are you can visit on click [here](https://help.github.com/en/github/working-with-github-pages/about-github-pages){:target="blank"} or [here](https://pages.github.com/){:target="blank"}

###### Source : [`Jekyll Docs`](https://jekyllrb.com/docs/)

> ### To know more and get started with Jekyll you can click [here](https://jekyllrb.com/)

# Installation

**Jekyll is a Ruby Gem, so you must have Ruby preinstalled.**

### Requirements

* [Ruby](https://www.ruby-lang.org/en/downloads/){:target="_blank"} version 2.5.0 or above, including all development headers (ruby version can be checked by running ruby -v)
* [Ruby Gems](https://rubygems.org/pages/download){:target="_blank"} (which you can check by running gem -v)
* [GCC](https://gcc.gnu.org/install/){:target="_blank"} and [Make](https://www.gnu.org/software/make/){:target="_blank"}

### After Installing the Requirements you can follow these guides:

**For detailed install instructions have a look at the guide for your operating system.**

* [macOS](https://jekyllrb.com/docs/installation/macos/){:target="_blank"}
* [Ubuntu](https://jekyllrb.com/docs/installation/ubuntu/){:target="_blank"}
* [Other Linux Distros](https://jekyllrb.com/docs/installation/other-linux/){:target="_blank"}
* [Windows](https://jekyllrb.com/docs/installation/windows/){:target="_blank"}

### Creating a new Jekyll site

**We can create a new Jekyll site just by a simple command:**

> `jekyll new <project-name>`

Jekyll will create a new directory named as `project-name` which is customizable. (i.e. simply change the name to anything you like)

* If you don't want a subdirectory, you can use `jekyll new .` to create the project in the current directory.

### Changing into the Directory

`cd` into the directory, or just remain in place if you are already there.

### Building the site and making it available on a local server

  > `jekyll serve` <br>

* Shortcut: `jekyll s`
* Some tutorials use `bundle exec jekyll serve` instead, but I don't see the point of doing this.

### Browsing your Jekyll site

> Open [`http://localhost:4000/`](http://localhost:4000/) in your browser

###### On encountering any problem while building and serving your Jekyll site you can consider visiting to the [troubleshooting](https://jekyllrb.com/docs/troubleshooting/#configuration-problems) page
