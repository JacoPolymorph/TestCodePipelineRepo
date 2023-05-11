import subprocess
import common
import os
from message_slack import message_slack_channel
cmd = ['ng', 'test', '--no-watch', '--no-progress', '--code-coverage', '--browsers', 'ChromeHeadlessNoSandbox',]


API_TOKEN = os.environ.get('SLACK_API_TOKEN')
REPORT_CHANNEL_ID = os.environ.get('REPORT_CHANNEL_ID')
TEST_RESULTS_URL = os.environ.get('TEST_RESULTS_URL')
BUILD_NUMBER = os.environ.get('CODEBUILD_BUILD_NUMBER')
COMMIT_ID = os.environ.get('CODEBUILD_RESOLVED_SOURCE_VERSION')
SOURCE_REPO_BASE_URL = os.environ.get('SOURCE_REPO_BASE_URL')




def run_tests() -> str:
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    stdout_str = res.stdout.decode()
    return stdout_str



# example output
# 19 04 2023 13:57:58.947:INFO [karma-server]: Karma v6.4.1 server started at http://localhost:9876/
# 19 04 2023 13:57:58.949:INFO [launcher]: Launching browsers ChromeHeadlessNoSandbox with concurrency unlimited
# 19 04 2023 13:57:58.977:INFO [launcher]: Starting browser ChromeHeadless
# 19 04 2023 13:58:00.068:INFO [Chrome Headless 112.0.5615.121 (Linux x86_64)]: Connected on socket *** with id ***
# Chrome Headless 112.0.5615.121 (Linux x86_64): Executed 0 of 4 SUCCESS (0 secs / 0 secs)
# Chrome Headless 112.0.5615.121 (Linux x86_64): Executed 1 of 4 SUCCESS (0 secs / 0.048 secs)
# Chrome Headless 112.0.5615.121 (Linux x86_64): Executed 2 of 4 SUCCESS (0 secs / 0.094 secs)
# Chrome Headless 112.0.5615.121 (Linux x86_64): Executed 3 of 4 SUCCESS (0 secs / 0.098 secs)
# Chrome Headless 112.0.5615.121 (Linux x86_64): Executed 4 of 4 SUCCESS (0 secs / 0.1 secs)
# Chrome Headless 112.0.5615.121 (Linux x86_64): Executed 4 of 4 SUCCESS (0.193 secs / 0.1 secs)
# TOTAL: 4 SUCCESS
#
# =============================== Coverage summary ===============================
# Statements   : 91.66% ( 11/12 )
# Branches     : 33.33% ( 1/3 )
# Functions    : 85.71% ( 6/7 )
# Lines        : 90.9% ( 10/11 )
# ================================================================================

def process_test_results(raw_test_results: str) -> str:
    allLines = [common.escape_ansi(line) for line in raw_test_results.splitlines()]

    summary_str = allLines[-9]
    agent_info = summary_str.split(":")[0]


    failedTests = [fail.split(agent_info)[1][1:] for fail in allLines[:-9] if agent_info in fail and fail.endswith("FAILED")]
    allTestsPassed = len(failedTests) == 0


    coverage = "\n".join(allLines[-6:])


    build_info_str = f'Fundza build {BUILD_NUMBER} from <{SOURCE_REPO_BASE_URL + "commit/" + COMMIT_ID}|{COMMIT_ID[:7]}>'

    out = [build_info_str, summary_str]
    if(not allTestsPassed):
        out.append("The following tests failed:")
        [out.append(f'\t{fail[:-7]}') for fail in failedTests]

    out.append(f'Detailed coverage report can be found <{TEST_RESULTS_URL}|here>')
    out.append(coverage)

    out = "\n".join(out)




if __name__ == '__main__':
    if (BUILD_NUMBER is None):
        print("This test script it not meant to run outside of a Codebuild pipeline.")
        print("You can test your code with code coverage by running ng test --code-coverage")
        exit(1)
    raw_test_results = run_tests()
    print(f'Raw test results:\n{raw_test_results}')
    print('-------------------------')
    processed_results = process_test_results(raw_test_results)
    print(f'Processed test results:\n{processed_results}')
    # message_slack_channel(api_token=API_TOKEN, channel=REPORT_CHANNEL_ID, message=processed_results)

    