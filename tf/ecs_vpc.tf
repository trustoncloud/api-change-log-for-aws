resource "aws_security_group" "nsg_task" {
  name        = "${var.app}-task"
  description = "Limit connections from internal resources while allowing ${var.app}-task to connect to all external resources"

  egress {
    from_port   = "0"
    to_port     = "0"
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.resource_tags
}
