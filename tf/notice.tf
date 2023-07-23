# ---------------------------------
# resources for SNS and CouldWatch
# ---------------------------------
resource "aws_sns_topic" "notice" {
  name = "ecs-errors"
}

resource "aws_cloudwatch_event_rule" "notice" {
  name        = "ecs-task-exit"
  description = "Captures exit event for ECS task."

  event_pattern = jsonencode({
    source: [
      "aws.ecs"
    ],
    detail-type: [
      "ECS Task State Change"
    ],
    detail: {
      lastStatus: [
        "STOPPED"
      ],
      stoppedReason: [
        "Essential container in task exited"
      ]
    }
  })
}

resource "aws_cloudwatch_event_target" "notice" {
  rule = aws_cloudwatch_event_rule.notice.name
  arn  = aws_sns_topic.notice.arn
}

resource "aws_sns_topic_policy" "default" {
  arn    = aws_sns_topic.notice.arn
  policy = data.aws_iam_policy_document.sns_topic_policy.json
}

data "aws_iam_policy_document" "sns_topic_policy" {
  statement {
    effect  = "Allow"
    actions = ["SNS:Publish"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    resources = [aws_sns_topic.notice.arn]
  }
}

resource "aws_sns_topic_subscription" "notice" {
  topic_arn = aws_sns_topic.notice.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.notice.arn
}

# -------------------------
# resources for AWS lambda.
# -------------------------
resource "aws_secretsmanager_secret" "notice" {
  name        = "slack/webhook"
  description = "Contains webhook to send error alerts to Slack."
}

resource "aws_secretsmanager_secret_version" "notice" {
  secret_id     = aws_secretsmanager_secret.notice.id
  secret_string = jsonencode(var.slack_webhook)
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "notice" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.notice.arn]
  }
}

resource "aws_iam_role" "notice" {
  name               = "error-reporter-lambda"
  description        = "Grants read access to secret value."
  assume_role_policy = data.aws_iam_policy_document.assume_role.json

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  ]

  inline_policy {
    name = "SecretReadAccessPolicy"
    policy = data.aws_iam_policy_document.notice.json
  }
}

data "archive_file" "notice_lambda" {
  type        = "zip"
  source_file = "notice.py"
  output_path = "lambda_code.zip"
}

resource "aws_lambda_function" "notice" {
  function_name = "error-reporter"
  description   = "Handles errors published to SNS topic."
  filename      = data.archive_file.notice_lambda.output_path
  role          = aws_iam_role.notice.arn
  handler       = "notice.handler"
  runtime       = "python3.9"

  source_code_hash = data.archive_file.notice_lambda.output_base64sha256

  environment {
    variables = {
      SLACK_WEBHOOK_SECRET_NAME = aws_secretsmanager_secret.notice.name
    }
  }
}

resource "aws_lambda_permission" "invoke_via_sns" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.notice.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.notice.arn
}
