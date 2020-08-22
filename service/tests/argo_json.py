"""
argo related json
"""

hello_world_wf_def = {
    "apiVersion": "argoproj.io/v1alpha1",
    "kind": "Workflow",
    "metadata": {
        "generateName": "hello-world-"
    },
    "spec":
        {
            "entrypoint":
                "whalesay",
            "templates":
                [
                    {
                        "name": "whalesay",
                        "container":
                            {
                                "image": "docker/whalesay",
                                "command": ["cowsay"],
                                "args": ["hello world"],
                                "resources":
                                    {
                                        "limits":
                                            {
                                                "memory": "32Mi",
                                                "cpu": "100m"
                                            }
                                    }
                            }
                    }
                ]
        }
}

hello_world_wf_running = {
    "metadata": {
        "name": "hello-world-a1234",
        "generateName": "hello-world-",
        "namespace": "argo",
        "selfLink": "/apis/argoproj.io/v1alpha1/namespaces/argo/workflows/hello-world-a1234",
        "uid": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa",
        "resourceVersion": "144305",
        "generation": 5,
        "creationTimestamp": "2222-02-22T04:13:17Z",
        "labels": {
            "workflows.argoproj.io/completed": "true",
            "workflows.argoproj.io/phase": "Succeeded"
        },
        "managedFields": [
            {
                "manager": "argo",
                "operation": "Update",
                "apiVersion": "argoproj.io/v1alpha1",
                "time": "2222-02-22T04:13:17Z",
                "fieldsType": "FieldsV1",
                "fieldsV1": {
                    "f:metadata": {
                        "f:generateName": {}
                    },
                    "f:spec": {
                        ".": {},
                        "f:arguments": {},
                        "f:entrypoint": {},
                        "f:serviceAccountName": {},
                        "f:templates": {}
                    },
                    "f:status": {}
                }
            },
            {
                "manager": "workflow-controller",
                "operation": "Update",
                "apiVersion": "argoproj.io/v1alpha1",
                "time": "2222-02-22T04:13:42Z",
                "fieldsType": "FieldsV1",
                "fieldsV1": {
                    "f:metadata": {
                        "f:labels": {
                            ".": {},
                            "f:workflows.argoproj.io/completed": {},
                            "f:workflows.argoproj.io/phase": {}
                        }
                    },
                    "f:spec": {
                        "f:ttlStrategy": {
                            ".": {},
                            "f:secondsAfterCompletion": {},
                            "f:secondsAfterSuccess": {}
                        }
                    },
                    "f:status": {
                        "f:conditions": {},
                        "f:finishedAt": {},
                        "f:nodes": {
                            ".": {},
                            "f:hello-world-a1234": {
                                ".": {},
                                "f:displayName": {},
                                "f:finishedAt": {},
                                "f:hostNodeName": {},
                                "f:id": {},
                                "f:name": {},
                                "f:outputs": {
                                    ".": {},
                                    "f:exitCode": {}
                                },
                                "f:phase": {},
                                "f:resourcesDuration": {
                                    ".": {},
                                    "f:cpu": {},
                                    "f:memory": {}
                                },
                                "f:startedAt": {},
                                "f:templateName": {},
                                "f:templateScope": {},
                                "f:type": {}
                            }
                        },
                        "f:phase": {},
                        "f:resourcesDuration": {
                            ".": {},
                            "f:cpu": {},
                            "f:memory": {}
                        },
                        "f:startedAt": {}
                    }
                }
            }
        ]
    },
    "spec": {
        "templates": [
            {
                "name": "whalesay",
                "arguments": {},
                "inputs": {},
                "outputs": {},
                "metadata": {},
                "container": {
                    "name": "",
                    "image": "docker/whalesay",
                    "command": [
                        "cowsay"
                    ],
                    "args": [
                        "hello world"
                    ],
                    "resources": {
                        "limits": {
                            "cpu": "100m",
                            "memory": "32Mi"
                        }
                    }
                }
            }
        ],
        "entrypoint": "whalesay",
        "arguments": {},
        "serviceAccountName": "argo"
    },
    "status": {
        "phase": "Succeeded",
        "startedAt": "2222-02-22T04:13:17Z",
        "finishedAt": "2222-02-22T04:13:42Z",
        "nodes": {
            "hello-world-a1234": {
                "id": "hello-world-a1234",
                "name": "hello-world-a1234",
                "displayName": "hello-world-a1234",
                "type": "Pod",
                "templateName": "whalesay",
                "templateScope": "local/hello-world-a1234",
                "phase": "Succeeded",
                "startedAt": "2222-02-22T04:13:17Z",
                "finishedAt": "2222-02-22T04:13:40Z",
                "resourcesDuration": {
                    "cpu": 22,
                    "memory": 22
                },
                "outputs": {
                    "exitCode": "0"
                },
                "hostNodeName": "localhost"
            }
        },
        "conditions": [
            {
                "type": "Completed",
                "status": "True"
            }
        ],
        "resourcesDuration": {
            "cpu": 22,
            "memory": 22
        }
    }
}


hello_world_wf_success = {
    "metadata": {
        "name": "hello-world-a1234",
        "generateName": "hello-world-",
        "namespace": "argo",
        "selfLink": "/apis/argoproj.io/v1alpha1/namespaces/argo/workflows/hello-world-a1234",
        "uid": "aaaaaaaa-1111-2222-3333-aaaaaaaaaaaa",
        "resourceVersion": "144305",
        "generation": 5,
        "creationTimestamp": "2222-02-22T04:13:17Z",
        "labels": {
            "workflows.argoproj.io/completed": "true",
            "workflows.argoproj.io/phase": "Succeeded"
        },
        "managedFields": [
            {
                "manager": "argo",
                "operation": "Update",
                "apiVersion": "argoproj.io/v1alpha1",
                "time": "2222-02-22T04:13:17Z",
                "fieldsType": "FieldsV1",
                "fieldsV1": {
                    "f:metadata": {
                        "f:generateName": {}
                    },
                    "f:spec": {
                        ".": {},
                        "f:arguments": {},
                        "f:entrypoint": {},
                        "f:serviceAccountName": {},
                        "f:templates": {}
                    },
                    "f:status": {}
                }
            },
            {
                "manager": "workflow-controller",
                "operation": "Update",
                "apiVersion": "argoproj.io/v1alpha1",
                "time": "2222-02-22T04:13:42Z",
                "fieldsType": "FieldsV1",
                "fieldsV1": {
                    "f:metadata": {
                        "f:labels": {
                            ".": {},
                            "f:workflows.argoproj.io/completed": {},
                            "f:workflows.argoproj.io/phase": {}
                        }
                    },
                    "f:spec": {
                        "f:ttlStrategy": {
                            ".": {},
                            "f:secondsAfterCompletion": {},
                            "f:secondsAfterSuccess": {}
                        }
                    },
                    "f:status": {
                        "f:conditions": {},
                        "f:finishedAt": {},
                        "f:nodes": {
                            ".": {},
                            "f:hello-world-a1234": {
                                ".": {},
                                "f:displayName": {},
                                "f:finishedAt": {},
                                "f:hostNodeName": {},
                                "f:id": {},
                                "f:name": {},
                                "f:outputs": {
                                    ".": {},
                                    "f:exitCode": {}
                                },
                                "f:phase": {},
                                "f:resourcesDuration": {
                                    ".": {},
                                    "f:cpu": {},
                                    "f:memory": {}
                                },
                                "f:startedAt": {},
                                "f:templateName": {},
                                "f:templateScope": {},
                                "f:type": {}
                            }
                        },
                        "f:phase": {},
                        "f:resourcesDuration": {
                            ".": {},
                            "f:cpu": {},
                            "f:memory": {}
                        },
                        "f:startedAt": {}
                    }
                }
            }
        ]
    },
    "spec": {
        "templates": [
            {
                "name": "whalesay",
                "arguments": {},
                "inputs": {},
                "outputs": {},
                "metadata": {},
                "container": {
                    "name": "",
                    "image": "docker/whalesay",
                    "command": [
                        "cowsay"
                    ],
                    "args": [
                        "hello world"
                    ],
                    "resources": {
                        "limits": {
                            "cpu": "100m",
                            "memory": "32Mi"
                        }
                    }
                }
            }
        ],
        "entrypoint": "whalesay",
        "arguments": {},
        "serviceAccountName": "argo"
    },
    "status": {
        "phase": "Succeeded",
        "startedAt": "2222-02-22T04:13:17Z",
        "finishedAt": "2222-02-22T04:13:42Z",
        "nodes": {
            "hello-world-a1234": {
                "id": "hello-world-a1234",
                "name": "hello-world-a1234",
                "displayName": "hello-world-a1234",
                "type": "Pod",
                "templateName": "whalesay",
                "templateScope": "local/hello-world-a1234",
                "phase": "Succeeded",
                "startedAt": "2222-02-22T04:13:17Z",
                "finishedAt": "2222-02-22T04:13:40Z",
                "resourcesDuration": {
                    "cpu": 22,
                    "memory": 22
                },
                "outputs": {
                    "exitCode": "0"
                },
                "hostNodeName": "localhost"
            }
        },
        "conditions": [
            {
                "type": "Completed",
                "status": "True"
            }
        ],
        "resourcesDuration": {
            "cpu": 22,
            "memory": 22
        }
    }
}
