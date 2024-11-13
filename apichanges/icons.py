import logging
import os
import tempfile
import urllib.request
import zipfile
from shutil import copy

from jinja2 import Template

from .exceptions import DirectoryNotFoundError

logging.basicConfig(format="%(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


ICON_SERVICE_MAP = {
    "toc": "ToC",
    "toc-cloud": "ToC-Cloud",
    "rss-feed": "RSS-Feed",
    "mailing-list": "Mailing-List",
    "aws": "AWS",
    "a4b": "Alexa-For-Business",
    "access-analyzer": "Identity-and-Access-Management",
    "acm": "Certificate-Manager",
    "acm-pca": "Certificate-Manager",
    "activate": "Activate",
    "amplify": "Amplify",
    "amplifybackend": "Amplify",
    "amplifyuibuilder": "Amplify",
    "apigateway": "API-Gateway",
    "apigatewayv2": "API-Gateway",
    "appconfig": "Systems-Manager",
    "appflow": "AppFlow",
    "application-autoscaling": "Application-Auto-Scaling",
    "applicationinsights": "CloudWatch",
    "appmesh": "App-Mesh",
    "apprunner": "App-Runner",
    "appstream": "Appstream",
    "appsync": "AppSync",
    "aps": "Managed-Service-For-Prometheus",
    "athena": "Athena",
    "auditmanager": "Audit-Manager",
    "autoscaling": "EC2-Auto-Scaling",
    "aws-marketplace": "Marketplace_Dark",
    "aws-marketplace-management": "Marketplace_Dark",
    "backup": "Backup",
    "backup-gateway": "Backup",
    "batch": "Batch",
    "braket": "Braket",
    "budgets": "Budgets",
    "ce": "Cost-Explorer",
    "chime": "Chime",
    "chatbot": "Chatbot",
    "cloud9": "Cloud9",
    "clouddirectory": "Cloud-Directory",
    "cloudformation": "CloudFormation",
    "cloudfront": "CloudFront",
    "cloudhsm": "CloudHSM",
    "cloudsearch": "CloudSearch",
    "cloudshell": "CloudShell",
    "cloudtrail": "CloudTrail",
    "cloudwatch": "CloudWatch",
    "codeartifact": "CodeArtifact",
    "codebuild": "CodeBuild",
    "codecommit": "CodeCommit",
    "codedeploy": "CodeDeploy",
    "codedeploy-commands-secure": "CodeDeploy",
    "codeguru": "CodeGuru",
    "codeguru-profiler": "CodeGuru",
    "codeguru-reviewer": "CodeGuru",
    "codepipeline": "CodePipeline",
    "codestar": "CodeStar",
    "codestar-connections": "CodeStar",
    "codestar-notifications": "CodeStar",
    "cognito-identity": "Cognito",
    "cognito-idp": "Cognito",
    "cognito-sync": "Cognito",
    "comprehend": "Comprehend",
    "comprehendmedical": "Comprehend",
    "compute-optimizer": "Compute-Optimizer",
    "config": "Config",
    "connect": "Connect",
    "cur": "Cost-and-Usage-Report",
    "databrew": "Glue-Databrew",
    "dataexchange": "Data-Exchange",
    "datapipeline": "Data-Pipeline",
    "datasync": "DataSync",
    "dax": "DynamoDB",
    "deepracer": "DeepRacer",
    "detective": "Detective",
    "devicefarm": "Device-Farm",
    "devops-guru": "DevOps-Guru",
    "directconnect": "Direct-Connect",
    "discovery": "Migration-Hub",
    "dlm": "Backup",
    "dms": "Database-Migration-Service",
    "ds": "Directory-Service",
    "dynamodb": "DynamoDB",
    "ebs": "Elastic-Block-Store-EBS",
    "ec2": "EC2",
    "ec2-instance-connect": "EC2",
    "ecr": "Elastic-Container-Registry",
    "ecr-public": "Elastic-Container-Registry",
    "ecs": "Elastic-Container-Service",
    "eks": "Elastic-Kubernetes-Service",
    "elastic-inference": "Elastic-Inference",
    "elasticache": "ElastiCache",
    "elasticbeanstalk": "Elastic-Beanstalk",
    "elasticfilesystem": "EFS",
    "elasticloadbalancing": "Elastic-Load-Balancing",
    "elasticloadbalancingv2": "Elastic-Load-Balancing",
    "elasticmapreduce": "EMR",
    "elastictranscoder": "Elastic-Transcoder",
    "elemental-activations": "Elemental-Appliances-&-Software",
    "elemental-appliances-software": "Elemental-Appliances-&-Software",
    "es": "OpenSearch-Service",
    "events": "EventBridge",
    "evidently": "CloudWatch",
    "execute-api": "API-Gateway",
    "finspace": "Finspace",
    "firehose": "Kinesis-Firehose",
    "fis": "Fault-Injection-Simulator",
    "fms": "Firewall-Manager",
    "forecast": "Forecast",
    "frauddetector": "Fraud-Detector",
    "freertos": "FreeRTOS",
    "fsx": "FSx",
    "gamelift": "GameLift",
    "geo": "Location-Service",
    "glacier": "Simple-Storage-Service-Glacier",
    "globalaccelerator": "Global-Accelerator",
    "glue": "Glue",
    "grafana": "Managed-Service-For-Grafana",
    "greengrass": "IoT-Greengrass",
    "greengrassv2": "IoT-Greengrass",
    "groundstation": "Ground-Station",
    "guardduty": "GuardDuty",
    "health": "Personal-Health-Dashboard",
    "healthlake": "HealthLake",
    "honeycode": "HoneyCode",
    "iam": "Identity-and-Access-Management",
    "imagebuilder": "EC2-Image-Builder",
    "importexport": "SnowBall",
    "inspector": "Inspector",
    "inspector2": "Inspector",
    "iot": "IoT-Core",
    "iot1click": "IoT-1-Click",
    "iotanalytics": "IoT-Analytics",
    "iotevents": "IoT-Events",
    "iotfleethub": "IoT-Core",
    "iotsitewise": "IoT-Sitewise",
    "iotthingsgraph": "IoT-Things-Graph",
    "iotwireless": "IoT-Core",
    "ivs": "Interactive-Video-Service",
    "kafka": "Managed-Streaming-For-Apache-Kafka",
    "kafkaconnect": "Managed-Streaming-For-Apache-Kafka",
    "kendra": "Kendra",
    "kinesis": "Kinesis",
    "kinesisanalytics": "Kinesis-Data-Analytics",
    "kinesisanalyticsv2": "Kinesis-Data-Analytics",
    "kinesisvideo": "Kinesis-Video-Streams",
    "kms": "Key-Management-Service",
    "lakeformation": "Lake-Formation",
    "lambda": "Lambda",
    "lex": "Lex",
    "lexv2": "Lex",
    "license-manager": "License-Manager",
    "lightsail": "Lightsail",
    "logs": "CloudWatch",
    "lookoutequipment": "Lookout-For-Equipment",
    "lookoutmetrics": "Lookout-For-Metrics",
    "lookoutvision": "Lookout-For-Vision",
    "machinelearning": "Machine-Learning",
    "macie": "Macie",
    "macie2": "Macie",
    "managedblockchain": "Managed-Blockchain",
    "marketplacecommerceanalytics": "Marketplace",
    "mediaconnect": "Elemental-MediaConnect",
    "mediaconvert": "Elemental-MediaConvert",
    "medialive": "Elemental-MediaLive",
    "mediapackage": "Elemental-MediaPackage",
    "mediapackage-vod": "Elemental-MediaPackage",
    "mediastore": "Elemental-MediaStore",
    "mediatailor": "Elemental-MediaTailor",
    "mgh": "Migration-Hub",
    "mgn": "Application-Migration-Service",
    "migrationhub-strategy": "Migration-Hub",
    "migrationhub-orchestrator": "Migration-Hub",
    "mobilehub": "Mobile",
    "mobileanalytics": "Mobile",
    "mobiletargeting": "Pinpoint",
    "monitron": "Monitron",
    "mq": "MQ",
    "networkmanager": "Virtual-Private-Cloud",
    "network-firewall": "Network-Firewall",
    "nimble": "Nimble-Studio",
    "oidc": "Single-Sign-On",
    "opsworks": "OpsWorks",
    "opsworks-cm": "OpsWorks",
    "organizations": "Organizations",
    "outposts": "Outposts-Rack",
    "panorama": "Panorama",
    "personalize": "Personalize",
    "pi": "CloudWatch",
    "polly": "Polly",
    "profile": "Connect",
    "proton": "Proton",
    "qldb": "Quantum-Ledger-Database",
    "quicksight": "Quicksight",
    "ram": "Resource-Access-Manager",
    "rds": "RDS",
    "rds-data": "Aurora",
    "redshift": "Redshift",
    "redshift-data": "Redshift",
    "refactor-spaces": "Migration-Hub",
    "rekognition": "Rekognition",
    "resource-groups": "Resource-Access-Manager",
    "resource-explorer": "Resource-Access-Manager",
    "robomaker": "RoboMaker",
    "route53": "Route-53",
    "route53domains": "Route-53",
    "route53resolver": "Route-53",
    "rum": "CloudWatch",
    "s3": "Simple-Storage-Service",
    "s3-outposts": "S3-On-Outposts",
    "sagemaker": "SageMaker",
    "savingsplans": "Savings-Plans",
    "schemas": "EventBridge",
    "sdb": "Database",
    "secretsmanager": "Secrets-Manager",
    "securityhub": "Security-Hub",
    "serverlessrepo": "Serverless-Application-Repository",
    "servicecatalog": "Service-Catalog",
    "servicediscovery": "Route-53",
    "servicequotas": "Trusted-Advisor",
    "ses": "Simple-Email-Service",
    "sesv2": "Simple-Email-Service",
    "shield": "Shield",
    "signer": "Signer",
    "sms": "Pinpoint",
    "sms-voice": "Pinpoint",
    "sms-voicev2": "Pinpoint",
    "snowball": "Snowball",
    "sns": "Simple-Notification-Service",
    "sqs": "Simple-Queue-Service",
    "ssm": "Systems-Manager",
    "ssm-incidents": "Systems-Manager",
    "ssm-contacts": "Systems-Manager",
    "ssm-guiconnect": "Systems-Manager",
    "sso": "Single-Sign-On",
    "states": "Step-Functions",
    "storagegateway": "Storage-Gateway",
    "sts": "Identity-and-Access-Management",
    "support": "Support",
    "swf": "Step-Functions",
    "textract": "Textract",
    "timestream": "Timestream",
    "transcribe": "Transcribe",
    "transfer": "Transfer-Family",
    "translate": "Translate",
    "trustedadvisor": "Trusted-Advisor",
    "waf": "WAF",
    "waf-regional": "WAF",
    "wafv2": "WAF",
    "wellarchitected": "Well-Itected-Tool",
    "workdocs": "WorkDocs",
    "worklink": "WorkLink",
    "workmail": "WorkMail",
    "workmailmessageflow": "WorkMail",
    "workspaces": "Workspaces",
    "workspaces-web": "Workspaces",
    "xray": "X-Ray",
}

ICON_TYPES = {"resource": "Resource", "category": "Category", "main": "Architecture"}

ICON_SIZES = ["16", "32", "48", "64", "256", "320"]

CSS_BUILD = """
{% for name, value in icons.items() %}
.{{ name }} {
    background-image: url('{{ value.path }}');
    min-width: {{ value.size }}px;
    min-height: {% if value.path.endswith('.svg') %}100%;
    {% else %}{{ value.size }}px;
    {% endif %}
}
{% endfor %}
"""


class IconBuilder:
    def __init__(self, url):
        self.assets_dir = os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "assets"
        )
        if not os.path.exists(self.assets_dir):
            raise DirectoryNotFoundError(f"Directory not found: {self.assets_dir}")

        with tempfile.TemporaryDirectory() as temp_dir:
            icons_dir = self.download_icons(url, temp_dir)
            self.icons = self.get_icons(icons_dir)
            self.collect_icons()

        self.build_css()

    def download_icons(self, url, target_dir) -> str:
        """Download and extract zip file from the given URL."""
        zip_path = os.path.join(target_dir, "icons.zip")
        icons_dirpath = os.path.join(target_dir, "icons")

        # Download the file from the URL
        logger.info("Downloading icons from: %s", url)
        urllib.request.urlretrieve(url, zip_path)

        # Extract the zip file
        logger.info("Extracting icons to: %s", icons_dirpath)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(icons_dirpath)

        return icons_dirpath

    def get_icons(self, icons_dir):
        icons = dict()
        if not os.path.isdir(icons_dir):
            raise DirectoryNotFoundError("Folder does not exist: %s", icons_dir)

        logger.info("Processing icons from directory: %s", icons_dir)
        for root, _, files in os.walk(icons_dir):
            if not any([x.endswith(".png") for x in files]):
                continue
            for itype, name in ICON_TYPES.items():
                if not any([x.startswith(name) for x in root.split("/")]):
                    continue
                for name in files:
                    if not name.endswith(".png"):
                        continue
                    new_name = (
                        name.replace(" ", "")
                        .replace("Arch_Amazon", str())
                        .replace("Arch_AWS", str())
                        .replace("Res_Amazon", str())
                        .replace("Res_AWS", str())
                        .replace("Arch", str())
                        .replace("Res_", str())
                        .lstrip("_")
                        .lstrip("-")
                        .lower()
                    )
                    if new_name.startswith("amazon"):
                        new_name = new_name.replace("amazon", str())

                    path = os.path.join(itype, new_name)
                    if path in icons.values():
                        base = os.path.basename(path)
                        dirname = os.path.dirname(path)
                        path = os.path.join(dirname, f"_{base}")
                    icons[os.path.join(root, name)] = path
        return icons

    def collect_icons(self):
        prefix_dir = os.path.join(self.assets_dir, "icons")
        logger.info("Collecting icons to directory: %s", prefix_dir)
        for src, dest in self.icons.items():
            path = os.path.join(prefix_dir, dest)
            dirname = os.path.dirname(path)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
            copy(src, path)

    def build_css(self):
        css_path = os.path.join(self.assets_dir, "css", "icons.css")
        dirname = os.path.dirname(css_path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)

        logger.info("Preparing and writing CSS to file: %s", css_path)
        icons = dict()
        for size in ICON_SIZES:
            for key, value in ICON_SERVICE_MAP.items():
                icon_dir = os.path.join(self.assets_dir, "icons")
                names = [
                    f"{value.lower()}.svg",
                    f"{value.lower()}.png",
                    value.lower()
                    + "_"
                    + ("64@5x" if size == "320" else "64@4x" if size == "256" else size)
                    + ".png",
                ]
                for icon_name in names:
                    if os.path.isfile(os.path.join(icon_dir, icon_name)):
                        icons[f"{key}-{size}"] = {
                            "size": size,
                            "path": os.path.join("/assets", "icons", icon_name),
                        }
                    elif os.path.isfile(os.path.join(icon_dir, "main", icon_name)):
                        icons[f"{key}-{size}"] = {
                            "size": size,
                            "path": os.path.join("/assets", "icons", "main", icon_name),
                        }

        with open(css_path, "w") as f:
            f.write(Template(CSS_BUILD, lstrip_blocks=True, trim_blocks=True).render(icons=icons))
