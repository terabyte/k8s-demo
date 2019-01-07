FROM quay.io/coreos/etcd:v3.3.10

EXPOSE 2379
CMD ["/usr/local/bin/etcd", "--name", "my-etcd-1", "--data-dir", "/etcd-data", "--listen-client-urls", "http://0.0.0.0:2379", "--advertise-client-urls", "http://${HOSTNAME}:2379", "--listen-peer-urls", "http://0.0.0.0:2380", "--initial-advertise-peer-urls", "http://${HOSTNAME}:2380", "--initial-cluster", "my-etcd-1=http://${HOSTNAME}:2380", "--initial-cluster-token", "my-etcd-token", "--initial-cluster-state", "new", "--auto-compaction-retention", "1" ]
