import aws_cdk as core
import aws_cdk.assertions as assertions

from smugmug_create_album.smugmug_create_album_stack import SmugmugCreateAlbumStack

# example tests. To run these tests, uncomment this file along with the example
# resource in smugmug_create_album/smugmug_create_album_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SmugmugCreateAlbumStack(app, "smugmug-create-album")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
