<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">

<h3 align="center">repoReporter</h3>

  <p align="center">
    A CLI application that generates a report via email about the Pull Requests activities along the specified period of time.
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This python based app makes requests to `Github API` and gets the pull requests activity data during the specified period of time (default to 7 days). The period of days and the path to the configuration file to be used can be passed in the command.

PR Data is classified into 3 categories `open`, `merged` and `closed`after that the data is formatted as an email which can be sent to a manager or Scrum master.

**NOTE:**
- SMTP server is not currently implemented instead of that a html file is generated containing the data that should be sent in the email.
- Data use to sent the email is printed to console.



<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [requests](https://requests.readthedocs.io/en/latest/)
* [jinja2](https://jinja.palletsprojects.com/en/3.0.x/templates/#builtin-filters)
* [fire](https://github.com/google/python-fire/tree/master)
  
  
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running you can follow 2 different paths with Docker or without Docker. The script calculates a datetime used like a low boundary to determine PRs to be considered, each cycle has a fixed time and once you have a call with no valid datetimes the requests ends.

### Prerequisites

For a low request rate GitHub does not enforce the usage of authentication, that's why is not being implemented here.

#### With Docker

You need to have Docker Engine (or Docker Desktop) installed, if not you can follow the [guides](https://docs.docker.com/engine/install/).

Using this path you can skip **Installation** section.

#### Without Docker

**WIP**

### Installation

#### With Docker

1. Clone the repo
```sh
git clone https://github.com/iscOlivares14/repoReporter.git
```
2. Build a local image
```sh
docker build -t reporeporter .
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

#### With Docker

Once the image has been created we can run the container as follows

1. Run a container setting a folder to store generated templates
```sh
# point a tm folder to the linux /tmp folder where the script place the templates
docker run -v $(pwd)/tmp:/tmp reporeporter
```


You can override two parameters that are used by the script:
- --period_days=<number of days, default: 7>
- --config_file_path='<relative path to config, default: config/config.yml>'

```sh
# override the period of days
docker run -v $(pwd)/tmp:/tmp reporeporter --period_days=20
```

```sh
# override both parameters this example points to pytest
docker run -v $(pwd)/tmp:/tmp reporeporter --period_days=20 --config_file_path='config/config_pytest.yml'
```


All of the commands above generates an output like this:
- Line 1) line shows the datatime used as a low boundary of the PRs to consider by the report
- Line 2) Shows the number of any type of PR in the iteration. One or more repetitions.
- Line 5) Shows the number of PRs by type after all iterations.
- Line 6) Shows data to be use at sending mail time.
- Line 7) Shows the path of the template created with the collected data to be sent.
```sh
INFO:repository:Valid datetime 2024-06-10 20:16:55.615238
INFO:repository:# Cycle - O: 3 / C: 2 / M: 8
INFO:repository:# Cycle - O: 0 / C: 0 / M: 0
INFO:repository:Stop extraction as no new valid events appeared
INFO:repository:Total <Open: 3> <Closed: 2> <Merged: 8>
INFO:__main__:{'to': 'pr_reports@company.com', 'from': 'reporter@company.com', 'subject': 'Pull Requests from last {days} days.', 'template_uri': 'template/pr_report.html'}
INFO:__main__:Templated genetared: /tmp/pytest-Github-2024-06-17 20:16:56.954512.html
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Refactor GitHUbRepo classes extracting the PR content into a Class
- [ ] Implement precommit 
- [ ] Implememt GitHub Actions for CI
    - [ ] Linting
    - [ ] Unit testing

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>
-->


