# Contributing to *ni-measurement-plugin-package-builder* 

Contributions to *ni-measurement-plugin-package-builder* are welcome from all!

*ni-measurement-plugin-package-builder* is managed via [git](https://git-scm.com), with the canonical upstream
repository hosted on [GitHub](https://github.com/ni/ni-measurement-plugin-package-builder).

*ni-measurement-plugin-package-builder* follows a pull-request model for development.  If
you wish to contribute, you will need to create a GitHub account, clone this
project, push a branch with your changes to your project, and then submit a
pull request.

See [GitHub's official documentation](https://help.github.com/articles/using-pull-requests/)
for more details.

**Important:** Commit titles and messages should adhere to the
[Angular style](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#commits)
to ensure proper semantic versioning.

# Getting Started

To contribute to this project, it is recommended that you follow these steps:

1. Clone this repository on GitHub.
2. Run the unit tests on your system (see Testing section). At this point,
   if any tests fail, do not begin development. Try to investigate these
   failures. If you're unable to do so, report an issue through our
   [GitHub issues page](https://github.com/ni/ni-measurement-plugin-package-builder/issues).
3. Write new tests that demonstrate your bug or feature. Ensure that these
   new tests fail.
4. Make your change.
5. Run all the unit tests again (which include the tests you just added),
   and confirm that they all pass.
6. Send a GitHub Pull Request to the main repository's master branch. GitHub
   Pull Requests are the expected method of code collaboration on this project.


# Setup virtual environement

You must have a supported version of Python (3.8+) and [Poetry](https://python-poetry.org/docs/) installed locally.

```
cd ni_measurement_plugin_package_builder

poetry env use Python
```

To run commands and scripts, spawn a shell within the virtual environment managed by Poetry:

```
poetry shell
```


# Developer Certificate of Origin (DCO)

   Developer's Certificate of Origin 1.1

   By making a contribution to this project, I certify that:

   (a) The contribution was created in whole or in part by me and I
       have the right to submit it under the open source license
       indicated in the file; or

   (b) The contribution is based upon previous work that, to the best
       of my knowledge, is covered under an appropriate open source
       license and I have the right under that license to submit that
       work with modifications, whether created in whole or in part
       by me, under the same open source license (unless I am
       permitted to submit under a different license), as indicated
       in the file; or

   (c) The contribution was provided directly to me by some other
       person who certified (a), (b) or (c) and I have not modified
       it.

   (d) I understand and agree that this project and the contribution
       are public and that a record of the contribution (including all
       personal information I submit with it, including my sign-off) is
       maintained indefinitely and may be redistributed consistent with
       this project or the open source license(s) involved.

(taken from [developercertificate.org](https://developercertificate.org/))

See [LICENSE](https://github.com/ni/ni-measurement-plugin-package-builder/blob/main/LICENSE)
for details about how *ni-measurement-plugin-package-builder* is licensed.