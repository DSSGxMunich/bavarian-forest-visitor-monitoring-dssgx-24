![Bavarian Forest Logo](src/streamlit_app/assets/logo-bavarian-forest-national-park.png)
# Harmonizing Tourism and Nature Protection in the Bavarian Forest National Park 🌲 

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_red.svg)](https://nationalpark-bayerischer-wald.streamlit.app/)

This repository includes the code and documentation for the project "*Harmonizing tourism and nature protection in the Bavarian Forest National Park*" by the fellowship program [Data Science for Social Good Munich, 2024](https://sites.google.com/view/dssgx-munich-2023/startseite).

## Project Overview 🌍 

### Background 📜

The Bavarian Forest National Park is a protected area in the Bavarian Forest in Bavaria, Germany. Since its foundation, the park has been a place for nature conservation and research. The park is also a popular tourist destination, attracting visitors over 1.4 million visitors per year from all over the world. The park is home to a wide variety of flora and fauna, including many rare and endangered species.

### Problem Statement 🎯

The park faces the challenge of balancing the needs of nature conservation with the demands of tourism. The park has installed a network of sensors (26 visitor counters and 12 parking sensors) to understand the flow of visitors which will optimize the visitor experience and protect the park's natural resources. This data is collected heterogeneously and needs to be unified and harmonized to provide insights for decision-making.

### Project Goal and Contributions 🚀

The goal of this project is to harmonize the data collected from the sensors in the Bavarian Forest National Park to provide insights for decision-making. 
We contribute to the project in the following ways:
1. Develop a data pipeline to harmonize the data collected from the all the different sensors and external sources.
2. Implement a predictive model to forecast the visitor traffic in the park for the coming week.
3. Develop a dashboard to visualize the data and insights for the park management, along with visualizing the forecasted visitor traffic from the predictive model.
4. Create technical documentation to provide insights on the data pipeline, predictive model and suggestions for future improvements in the project.

![Overall Solution](docs/asset/overall-dashboard.gif)
_A glimpse of the final dashboard ✨_

## How to use the code 🛠️

### Run Dashboard and Pipeline via a Docker Container

1. Clone the repository:
   ```bash
   git clone https://github.com/DSSGxMunich/bavarian-forest-visitor-monitoring-dssgx-24.git
    ```
2. Download Docker Desktop from [here](https://www.docker.com/products/docker-desktop/) and install it.

3. **Run the container via make:**

    a. **Make sure to have `make` installed.** If not, install it (e.g., with Homebrew for macOS - `brew install make`).

    b. **Authenticate with AWS:** As the project is loading and writing data to a configured AWS S3 object storage, either add AWS permanent credentials (`AWS_ACCESS_KEY_ID`and `AWS_ACCESS_KEY_ID`) to the [Makefile](Makefile), or specify to load them as environmental variables (as currently set up and the preferred option due to security reasons). Alternatively, configure the AWS CLI with Single-Sign-On (SSO), follow the instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html). For example, when using AWS SSO, run the following command to login:

    ```bash
    aws sso login --profile my-dev-aws-profile
    ```

    c. **Run the Dashboard:** Run the following command to build and run the Streamlit dashboard:
    ```bash
    make streamlit
    ```
    [!NOTE]  If you want to run the bash shell in the docker container, run the following command:
    ```bash
    make container
    ```
4. **Run the container without `make`:**

    a. **Authenticate with AWS:** As the project is loading and writing data to a configured AWS S3 object storage, either add AWS permanent credentials (`AWS_ACCESS_KEY_ID`and `AWS_ACCESS_KEY_ID`) to the [Makefile](Makefile), or specify to load them as environmental variables (as currently set up and the preferred option due to security reasons). Alternatively, configure the AWS CLI with Single-Sign-On (SSO), follow the instructions [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html). For example, when using AWS SSO, run the following command to login:

    ```bash
    aws sso login --profile my-dev-aws-profile
    ```


    c. **Run the `docker run` command** to run a container based on the previously built image. For further details on how to specify the `run` command, check the [Makefile](Makefile).

### Run Notebooks and General Code in a Local, Virtual Environment

Choose a virtual environment tool of your choice and install the dependencies of the respective requirements file, e.g. [requirements.txt](requirements.txt) (for the dashboard), [notebooks-requirements.txt](notebooks-requirements.txt) (for the notebooks), or [docs-requirements.txt](docs-requirements.txt) (for the documentation) from the root of the repository. In the following, you see the steps to create a virtual environment with a particularly, specified Python version with `pyenv` and the plugin `pyenv-virtualenv`.

1.  Install `pyenv-virtualenv`. Follow a tutorial to install `pyenv` and the plugin `pyenv-virtualenv`, e.g. follow [this tutorial](https://medium.com/@adocquin/mastering-python-virtual-environments-with-pyenv-and-pyenv-virtualenv-c4e017c0b173).

2. Create a virtual environment with a specified Python version.
    ```bash
    pyenv virtualenv {selected-python-version} {name-of-virtual-environment}
    ```
3. Activate the virtual environment.
    ```bash
    pyenv activate {name-of-virtual-environment}
    ```
4. Install the dependencies of the [requirements.txt](requirements.txt) in the root of the repository.
    ```bash
    pip install -r requirements.txt
    ```
#### Run Jupyter Notebooks

1. **Add the virtual environment as Jupyter kernel**

    In order to be able to run Jupyter notebooks in the created virtual environment, you need to specify a new kernel to be used by Jupyter making use of your virtual environment. Run the following command in the CLI by specifying a name for the kernel:

    ```
    python -m ipykernel install --user --name={name-for-kernel}
    ```

2. **Open Jupyter notebook**

    Either run the following command in the CLI to trigger the pop-up of the Jupyter interface in your browser:

    ```
    jupyter notebook
    ```

    OR: In case you are keen on using Jupyter Notebooks in the IDE VS Code, open the Jupyter Notebook in VS Code. (Tip: this way you can use all other VS Code features in notebooks, for example nice code highlighting, AI Coding features, etc.)

3. **Select kernel**

    In both the Jupyter UI and the notebook in VS Code, you need to select the specified kernel from before running the cells.

4. **Run the notebooks**

    Now go ahead and run the notebooks! :)

## Structure of the Repository 📁

The repository is structured as follows:

```
bavarian-forest-visitor-monitoring-dssgx-24/
│
├── assets/                 # Contains images and other assets for the README
│
├── data/                   # Contains the data used in the project
│
├── docs/                   # Contains the technical documentation
│
├── notebooks/              # Contains the notebooks for the data pipeline and predictive model
│
├── src/                    # Contains the source code for the data pipeline and predictive model
│
├── pages/                  # Contains the additional pages for the streamlit dashboard
│
├── Makefile                # Contains the commands to run the code
│
├── README.md               # Contains the information about the project
│
├── requirements.txt        # Contains the dependencies of the project
│
└── Dashboard.py            # Contains the code for the calling the predictive model and the streamlit dashboard
```

## Technical Documentation 📚

The technical documentation website is available [here](https://dssgxmunich.github.io/bavarian-forest-visitor-monitoring-dssgx-24/). 

## How to contribute to the project 🤝

Follow the following steps to contribute to the project:

1. Fork the repository to your GitHub account.
2. Create a new branch with a descriptive name for the feature you want to contribute to.
3. Make changes to the code or documentation.
4. Commit the changes to your branch.
5. Push the changes to your forked repository.
6. Create a pull request to the main repository.

NOTE: Be sure to merge the latest from the `upstream` before making a pull request!

### Requesting new features or reporting bugs 🐞

If you have any suggestions for new features or find any bugs, please [create an issue](https://github.com/DSSGxMunich/bavarian-forest-visitor-monitoring-dssgx-24/issues/new) in the repository. We are open to feedback and contributions! 🙏

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


