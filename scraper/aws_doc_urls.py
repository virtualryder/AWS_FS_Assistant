"""
Curated seed URLs and crawl boundary rules for AWS documentation sources.
Enhanced for financial services: includes security, compliance, AI/ML, and
data services most relevant to banks, insurers, fintechs, and payment processors.
"""

# Domains allowed during crawling
ALLOWED_DOMAINS = {
    "docs.aws.amazon.com",
    "aws.amazon.com",
}

# URL path prefixes that define the crawl boundary per source.
CRAWL_BOUNDARIES = {
    "docs.aws.amazon.com": [
        "/lambda/",
        "/AmazonS3/",
        "/AmazonRDS/",
        "/AWSEC2/",
        "/AmazonECS/",
        "/eks/",
        "/vpc/",
        "/IAM/",
        "/AWSCloudFormation/",
        "/sagemaker/",
        "/glue/",
        "/kinesis/",
        "/amazondynamodb/",
        "/redshift/",
        "/sns/",
        "/AWSSimpleQueueService/",
        "/apigateway/",
        "/AmazonCloudWatch/",
        "/step-functions/",
        "/eventbridge/",
        "/bedrock/",
        "/bedrock-agentcore/",
        "/transfer/",
        "/datasync/",
        "/storagegateway/",
        "/efs/",
        "/fsx/",
        "/AmazonElastiCache/",
        "/kms/",
        "/cognito/",
        "/guardduty/",
        "/securityhub/",
        "/waf/",
        "/athena/",
        "/emr/",
        "/quicksight/",
        "/codecommit/",
        "/codebuild/",
        "/codedeploy/",
        "/codepipeline/",
        "/cloudtrail/",
        "/config/",
        "/organizations/",
        "/systems-manager/",
        "/route53/",
        "/cloudfront/",
        "/elasticloadbalancing/",
        "/msk/",
        "/opensearch-service/",
        "/comprehend/",
        "/rekognition/",
        "/textract/",
        "/translate/",
        "/lex/",
        "/polly/",
        "/transcribe/",
        "/forecast/",
        "/personalize/",
        "/cdk/",
        "/appflow/",
        # Financial services security additions
        "/macie/",
        "/shield/",
        "/artifact/",
        "/aws-backup/",
        "/directconnect/",
        "/privatelink/",
        "/network-firewall/",
        "/detective/",
        "/inspector/",
        "/auditmanager/",
        "/acm-pca/",
        "/controltower/",
        "/access-analyzer/",
        "/ram/",
        "/sso/",
        "/identitystore/",
        "/connect/",
        "/AmazonS3Vectors/",
    ],
    "aws.amazon.com": [
        "/solutions/",
        "/prescriptive-guidance/",
        "/architecture/",
        "/financial-services/",
        "/compliance/",
    ],
}

# Seed URLs organised by source key.
SEED_URLS = {
    # ── Compute ────────────────────────────────────────────────────────────
    "lambda": {
        "name": "AWS Lambda Developer Guide",
        "url": "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "ec2": {
        "name": "Amazon EC2 User Guide",
        "url": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "ecs": {
        "name": "Amazon ECS Developer Guide",
        "url": "https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "eks": {
        "name": "Amazon EKS User Guide",
        "url": "https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Storage ────────────────────────────────────────────────────────────
    "s3": {
        "name": "Amazon S3 User Guide",
        "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "efs": {
        "name": "Amazon EFS User Guide",
        "url": "https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Database ───────────────────────────────────────────────────────────
    "rds": {
        "name": "Amazon RDS User Guide",
        "url": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "dynamodb": {
        "name": "Amazon DynamoDB Developer Guide",
        "url": "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "redshift": {
        "name": "Amazon Redshift Database Developer Guide",
        "url": "https://docs.aws.amazon.com/redshift/latest/dg/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "elasticache": {
        "name": "Amazon ElastiCache User Guide",
        "url": "https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Networking ─────────────────────────────────────────────────────────
    "vpc": {
        "name": "Amazon VPC User Guide",
        "url": "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "route53": {
        "name": "Amazon Route 53 Developer Guide",
        "url": "https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "cloudfront": {
        "name": "Amazon CloudFront Developer Guide",
        "url": "https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "api_gateway": {
        "name": "Amazon API Gateway Developer Guide",
        "url": "https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "direct_connect": {
        "name": "AWS Direct Connect User Guide",
        "url": "https://docs.aws.amazon.com/directconnect/latest/UserGuide/Welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "privatelink": {
        "name": "AWS PrivateLink User Guide",
        "url": "https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "network_firewall": {
        "name": "AWS Network Firewall Developer Guide",
        "url": "https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "global_accelerator": {
        "name": "AWS Global Accelerator Developer Guide",
        "url": "https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Security & Identity (Financial Services Priority) ──────────────────
    "iam": {
        "name": "AWS IAM User Guide",
        "url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "iam_identity_center": {
        "name": "AWS IAM Identity Center User Guide",
        "url": "https://docs.aws.amazon.com/singlesignon/latest/userguide/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "kms": {
        "name": "AWS KMS Developer Guide",
        "url": "https://docs.aws.amazon.com/kms/latest/developerguide/overview.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "cloudhsm": {
        "name": "AWS CloudHSM User Guide",
        "url": "https://docs.aws.amazon.com/cloudhsm/latest/userguide/introduction.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "cognito": {
        "name": "Amazon Cognito Developer Guide",
        "url": "https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "guardduty": {
        "name": "Amazon GuardDuty User Guide",
        "url": "https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "securityhub": {
        "name": "AWS Security Hub User Guide",
        "url": "https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "macie": {
        "name": "Amazon Macie User Guide",
        "url": "https://docs.aws.amazon.com/macie/latest/user/what-is-macie.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "detective": {
        "name": "Amazon Detective User Guide",
        "url": "https://docs.aws.amazon.com/detective/latest/userguide/detective-overview.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "inspector": {
        "name": "Amazon Inspector User Guide",
        "url": "https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "shield": {
        "name": "AWS Shield Developer Guide",
        "url": "https://docs.aws.amazon.com/waf/latest/developerguide/shield-chapter.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "waf": {
        "name": "AWS WAF Developer Guide",
        "url": "https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "access_analyzer": {
        "name": "AWS IAM Access Analyzer User Guide",
        "url": "https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Compliance & Audit (Financial Services Core) ───────────────────────
    "artifact": {
        "name": "AWS Artifact User Guide",
        "url": "https://docs.aws.amazon.com/artifact/latest/ug/what-is-aws-artifact.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "audit_manager": {
        "name": "AWS Audit Manager User Guide",
        "url": "https://docs.aws.amazon.com/audit-manager/latest/userguide/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "config": {
        "name": "AWS Config Developer Guide",
        "url": "https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "control_tower": {
        "name": "AWS Control Tower User Guide",
        "url": "https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "cloudtrail": {
        "name": "AWS CloudTrail User Guide",
        "url": "https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "organizations": {
        "name": "AWS Organizations User Guide",
        "url": "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "backup": {
        "name": "AWS Backup Developer Guide",
        "url": "https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Analytics & Data ───────────────────────────────────────────────────
    "glue": {
        "name": "AWS Glue Developer Guide",
        "url": "https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "kinesis": {
        "name": "Amazon Kinesis Data Streams Developer Guide",
        "url": "https://docs.aws.amazon.com/streams/latest/dev/introduction.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "athena": {
        "name": "Amazon Athena User Guide",
        "url": "https://docs.aws.amazon.com/athena/latest/ug/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "lakeformation": {
        "name": "AWS Lake Formation Developer Guide",
        "url": "https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Integration ────────────────────────────────────────────────────────
    "sqs": {
        "name": "Amazon SQS Developer Guide",
        "url": "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "sns": {
        "name": "Amazon SNS Developer Guide",
        "url": "https://docs.aws.amazon.com/sns/latest/dg/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "eventbridge": {
        "name": "Amazon EventBridge User Guide",
        "url": "https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "step_functions": {
        "name": "AWS Step Functions Developer Guide",
        "url": "https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── AI / ML (Financial Services Core) ─────────────────────────────────
    "sagemaker": {
        "name": "Amazon SageMaker Developer Guide",
        "url": "https://docs.aws.amazon.com/sagemaker/latest/dg/whatis.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "bedrock": {
        "name": "Amazon Bedrock User Guide",
        "url": "https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html",
        "source_label": "Amazon Bedrock Documentation",
        "tier": 1,
    },
    "bedrock_agentcore": {
        "name": "Amazon Bedrock AgentCore Developer Guide",
        "url": "https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html",
        "source_label": "Amazon Bedrock AgentCore Documentation",
        "tier": 1,
    },
    "a2i": {
        "name": "Amazon Augmented AI (A2I) Developer Guide",
        "url": "https://docs.aws.amazon.com/sagemaker/latest/dg/a2i-use-augmented-ai-a2i-human-review-loops.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "comprehend": {
        "name": "Amazon Comprehend Developer Guide",
        "url": "https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "textract": {
        "name": "Amazon Textract Developer Guide",
        "url": "https://docs.aws.amazon.com/textract/latest/dg/what-is-textract.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── DevOps & Management ────────────────────────────────────────────────
    "cloudformation": {
        "name": "AWS CloudFormation User Guide",
        "url": "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "cloudwatch": {
        "name": "Amazon CloudWatch User Guide",
        "url": "https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "systems_manager": {
        "name": "AWS Systems Manager User Guide",
        "url": "https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "secrets_manager": {
        "name": "AWS Secrets Manager User Guide",
        "url": "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "codepipeline": {
        "name": "AWS CodePipeline User Guide",
        "url": "https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "codebuild": {
        "name": "AWS CodeBuild User Guide",
        "url": "https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "cdk": {
        "name": "AWS CDK Developer Guide",
        "url": "https://docs.aws.amazon.com/cdk/v2/guide/home.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Special Sources ────────────────────────────────────────────────────
    "prescriptive_guidance": {
        "name": "AWS Prescriptive Guidance",
        "url": "https://aws.amazon.com/prescriptive-guidance/",
        "source_label": "AWS Prescriptive Guidance",
        "tier": 2,
    },
    "solutions_library": {
        "name": "AWS Solutions Library",
        "url": "https://aws.amazon.com/solutions/",
        "source_label": "AWS Solutions Library",
        "tier": 3,
    },
    "reference_architecture": {
        "name": "AWS Reference Architecture",
        "url": "https://aws.amazon.com/architecture/",
        "source_label": "AWS Reference Architecture",
        "tier": 2,
    },
    "financial_services": {
        "name": "AWS Financial Services Solutions",
        "url": "https://aws.amazon.com/financial-services/",
        "source_label": "AWS Financial Services",
        "tier": 2,
    },
    # ── Extended AI / ML ───────────────────────────────────────────────────
    "rekognition": {
        "name": "Amazon Rekognition Developer Guide",
        "url": "https://docs.aws.amazon.com/rekognition/latest/dg/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "transcribe": {
        "name": "Amazon Transcribe Developer Guide",
        "url": "https://docs.aws.amazon.com/transcribe/latest/dg/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "lex": {
        "name": "Amazon Lex Developer Guide",
        "url": "https://docs.aws.amazon.com/lexv2/latest/dg/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "connect": {
        "name": "Amazon Connect Administrator Guide",
        "url": "https://docs.aws.amazon.com/connect/latest/adminguide/what-is-amazon-connect.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "forecast": {
        "name": "Amazon Forecast Developer Guide",
        "url": "https://docs.aws.amazon.com/forecast/latest/dg/what-is-forecast.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Extended Analytics ─────────────────────────────────────────────────
    "emr": {
        "name": "Amazon EMR Management Guide",
        "url": "https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "quicksight": {
        "name": "Amazon QuickSight User Guide",
        "url": "https://docs.aws.amazon.com/quicksight/latest/user/welcome.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "opensearch": {
        "name": "Amazon OpenSearch Service Developer Guide",
        "url": "https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    # ── Extended Storage & Transfer ────────────────────────────────────────
    "fsx": {
        "name": "Amazon FSx for Windows File Server",
        "url": "https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "transfer": {
        "name": "AWS Transfer Family User Guide",
        "url": "https://docs.aws.amazon.com/transfer/latest/userguide/what-is-aws-transfer-family.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
    "datasync": {
        "name": "AWS DataSync User Guide",
        "url": "https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html",
        "source_label": "AWS Documentation",
        "tier": 1,
    },
}

# Maps topic keywords to one or more seed keys.
TOPIC_KEYWORD_MAP = {
    # Financial services specific
    "financial services": ["financial_services", "prescriptive_guidance", "solutions_library"],
    "banking": ["financial_services", "prescriptive_guidance", "rds", "kms", "guardduty"],
    "compliance": ["config", "audit_manager", "artifact", "securityhub", "cloudtrail", "control_tower"],
    "glba": ["macie", "kms", "guardduty", "cloudtrail", "config", "securityhub"],
    "pci dss": ["vpc", "kms", "waf", "shield", "cloudtrail", "securityhub", "macie"],
    "pci": ["vpc", "kms", "waf", "shield", "cloudtrail", "securityhub", "macie"],
    "sox": ["cloudtrail", "config", "organizations", "codepipeline", "securityhub"],
    "ffiec": ["cloudtrail", "securityhub", "config", "guardduty", "backup"],
    "model risk": ["sagemaker", "bedrock", "a2i"],
    "fraud detection": ["sagemaker", "kinesis", "dynamodb", "bedrock"],
    "aml": ["sagemaker", "kinesis", "opensearch", "comprehend"],
    "payment": ["sqs", "kinesis", "rds", "kms", "waf", "vpc"],
    "document processing": ["textract", "comprehend", "bedrock", "s3"],
    "zero trust": ["iam", "iam_identity_center", "vpc", "access_analyzer", "organizations"],
    # Core technology
    "serverless": ["lambda", "api_gateway", "step_functions", "eventbridge", "sqs", "sns"],
    "data pipeline": ["glue", "kinesis", "step_functions", "s3", "athena"],
    "data lake": ["s3", "glue", "athena", "redshift", "lakeformation"],
    "machine learning": ["sagemaker", "bedrock", "s3"],
    "ml": ["sagemaker", "bedrock", "s3"],
    "ai": ["bedrock", "bedrock_agentcore", "sagemaker"],
    "generative ai": ["bedrock", "bedrock_agentcore", "a2i"],
    "genai": ["bedrock", "bedrock_agentcore", "a2i"],
    "agent": ["bedrock_agentcore", "bedrock", "step_functions", "lambda"],
    "rag": ["bedrock", "opensearch", "s3", "kms"],
    "containers": ["ecs", "eks", "ec2"],
    "kubernetes": ["eks"],
    "database": ["rds", "dynamodb", "redshift", "elasticache"],
    "encryption": ["kms", "cloudhsm", "s3", "rds"],
    "security": ["iam", "kms", "cognito", "guardduty", "securityhub", "macie", "inspector", "waf", "shield"],
    "networking": ["vpc", "route53", "cloudfront", "api_gateway", "privatelink", "network_firewall"],
    "storage": ["s3", "efs", "elasticache"],
    "analytics": ["athena", "kinesis", "glue", "redshift", "quicksight"],
    "monitoring": ["cloudwatch", "cloudtrail", "securityhub"],
    "devops": ["cloudformation", "cloudwatch", "cloudtrail", "codepipeline"],
    "messaging": ["sqs", "sns", "eventbridge"],
    "api": ["api_gateway", "lambda"],
    "migration": ["prescriptive_guidance"],
    "nlp": ["comprehend", "lex", "transcribe"],
    "contact center": ["connect", "lex", "transcribe", "bedrock"],
    "search": ["opensearch"],
    "ci/cd": ["codebuild", "codepipeline", "cdk"],
    "infrastructure as code": ["cloudformation", "cdk"],
    "disaster recovery": ["backup", "rds", "route53", "global_accelerator"],
    "dr": ["backup", "rds", "route53", "global_accelerator"],
    "backup": ["backup", "rds", "s3"],
    "secrets": ["secrets_manager", "kms", "systems_manager"],
    "audit": ["cloudtrail", "audit_manager", "artifact", "config"],
}

# ── Canonical seed-key groupings ──────────────────────────────────────────────

# Automatically indexed at boot by startup_ingest.py.
# Financial services priority: security, compliance, and AI services lead.
PRIMARY_SEED_KEYS: list[str] = [
    # Core Compute & Containers
    "lambda", "ec2", "ecs", "eks",
    # Storage
    "s3",
    # Databases
    "rds", "dynamodb", "redshift", "elasticache",
    # Networking
    "vpc", "cloudfront", "api_gateway", "privatelink",
    # Security & Identity (Financial Services Core)
    "iam", "iam_identity_center", "kms", "cognito", "guardduty",
    "securityhub", "macie", "waf",
    # Compliance & Audit (Financial Services Core)
    "cloudtrail", "config", "audit_manager", "backup",
    # Analytics & Data
    "glue", "kinesis", "athena",
    # Messaging & Integration
    "sqs", "sns", "eventbridge", "step_functions",
    # AI / ML (Financial Services Core)
    "sagemaker", "bedrock", "bedrock_agentcore", "a2i",
    # DevOps & Management
    "cloudformation", "cloudwatch", "secrets_manager",
    # Organizations & Governance
    "organizations", "control_tower",
    # AWS Guidance & Financial Services (added to default index)
    "prescriptive_guidance", "solutions_library", "reference_architecture",
    "financial_services",
]

# Available for optional manual ingestion via the sidebar.
OPTIONAL_SEED_KEYS: list[str] = [
    # Extended Security & Compliance
    "cloudhsm", "shield", "network_firewall", "inspector", "detective",
    "access_analyzer", "artifact",
    # Extended AI / ML
    "comprehend", "rekognition", "transcribe", "textract", "lex",
    "connect", "forecast",
    # Extended Analytics
    "emr", "quicksight", "opensearch", "lakeformation",
    # Extended DevOps
    "codebuild", "codepipeline", "cdk",
    # Extended Networking
    "route53", "direct_connect", "global_accelerator",
    # Extended Storage & Transfer
    "efs", "fsx", "transfer", "datasync",
    # Extended Management
    "systems_manager",
    # Guidance & Solutions
    "prescriptive_guidance", "solutions_library", "reference_architecture",
    "financial_services",
]
