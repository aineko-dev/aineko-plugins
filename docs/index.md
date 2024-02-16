# Introduction to plugins

Aineko comes with a set of optional plugins that can be added to your pipeline. Currently these plugins are extra nodes with a focus on popular use-cases and best-practice patterns.
To use one of these nodes, simply add it to your dependencies and reference it in the pipeline configuration.

## Adding Dependencies


To add a plugin to your pipeline, you need to install it as a dependency. If you already have an Aineko project, you can add the plugin by executing `poetry add aineko-plugins-plugin-name`. For example to add the `fastapi-server` node, you would run `poetry add aineko-plugins-nodes-fastapi-server`.

## Reference in Pipeline Configuration

To use such a node, simply reference the class in your pipeline configuration.

:
    ```yaml title="pipeline.yml"
    nodes:
      fastapi:
        class: aineko_plugins.nodes.fastapi_server.FastAPI
        inputs:
          - test_sequence
        node_params:
          app: my_awesome_pipeline.fastapi:app
          port: 8000
    ```

Refer to the in-depth pages on each extra node for more detail on how to use them.
