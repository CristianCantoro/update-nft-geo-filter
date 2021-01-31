# nftables geoip filter

Scripts to update nftables geoip filter.

These scripts are based on [`nft-geo-filter`](https://github.com/rpthms/nft-geo-filter).

## Directories and files

```plain
.
├── files
│   ├── etc
│   │   └── update-nft-geo-filter.conf
│   └── usr
│       └── local
│           └── bin
│               └── update-nft-geo-filter
├── LICENSE
├── README.md
└── utils
    ├── config.sample.yaml
    ├── ngf-parse-log.py
    └── requirements.txt
```

## How to install

1. Clone the repo:

```bash
git clone git@github.com:CristianCantoro/ssh-geoip-filter.git
```

2. Get into the repo directory: `cd ssh-geoip-filter`

3. Copy:

    * `files/etc/update-nft-geo-filter.conf` to
      `/etc/update-nft-geo-filter.conf`
    * `files/usr/local/bin/update-nft-geo-filter` to
      `/usr/local/bin/update-nft-geo-filter`
    (you will need administrative privilege to perform these copies)

4. Update the configuration file at `/etc/update-nft-geo-filter.conf` and set
the values of the variables.

5. Test if `sshfilter` is working:

```bash
$ sshfilter -v 8.8.8.8
[2018-04-24_14:15:45][info]	DENY sshd connection from 8.8.8.8 (US)
```

You can also check the logs at `/var/log/auth.log`:

```bash
$ [sudo] tail -n1 /var/log/auth.log
Apr 24 14:15:45 inara cristian: DENY sshd connection from 8.8.8.8 (US)
```

6. Copy `files/etc/hosts.allow` and `files/etc/hosts.deny` to
   `/etc/hosts.allow` and `/etc/hosts.deny` respectively

7. Add a crontab job (as root) to update the geoip database:

```bash
(sudo crontab -l && echo '
# Update GeoIP database every 15 days
05  06  */15   *    *     /usr/local/bin/update-geoip >> /var/log/geoip.log
') | sudo crontab -
```

## Utils

The script `ngf-parse-log.py` parses timestamps from log file to convert them
to ISO format, so they are easier to process.

`sgf-parse-log.py`:

```bash
Parse timestamps from log file to convert it to ISO.

Usage:
  ngf-parse-log.py [--tz=TIMEZONE] [--prefix=PREFIX] [--config=CONFIG]
                   [--time-format=TIME_FORMAT]...
                   [<logfile>]...
  ngf-parse-log.py (-h | --help)
  ngf-parse-log.py --version

Argiments:
  <logfile>                     Log file to read [default: stdin].

Options:
  --config=CONFIG               Configuration file for ipinfo.io
                                [default: config.yaml]
  --prefix=PREFIX               Search prefix in logs [default: geo-filter].
  --tz=TIMEZONE                 Timezone of the timestamps in the log file
                                [default: America/Toronto].
  --time-format=TIME_FORMAT     Time format of the timestamps in the log file
                                [default: YYYY-MMM-DDTHH:mm:ss].
                                It can be specified multiple times.
  -h --help                     Show this screen.
  --version                     Show version.
```

Example usage:

* sample data:

```bash
$ grep 'geo-filter DROP' /var/log/syslog | tail -n5
an 31 12:44:03 river kernel: [260618.278101] geo-filter DROP IN=enp2s0 OUT= MAC=00:01:c0:0c:b0:a1:10:13:31:cb:27:48:08:00 SRC=194.147.140.24 DST=192.168.1.2 LEN=40 TOS=0x00 PREC=0x00 TTL=242 ID=64299 PROTO=TCP SPT=59582 DPT=11027 WINDOW=1024 RES=0x00 SYN URGP=0 
Jan 31 12:44:31 river kernel: [260646.444304] geo-filter DROP IN=enp2s0 OUT= MAC=00:01:c0:0c:b0:a1:10:13:31:cb:27:48:08:00 SRC=194.147.140.21 DST=192.168.1.2 LEN=40 TOS=0x00 PREC=0x00 TTL=242 ID=44168 PROTO=TCP SPT=58507 DPT=41390 WINDOW=1024 RES=0x00 SYN URGP=0 
Jan 31 12:45:40 river kernel: [260715.128307] geo-filter DROP IN=enp2s0 OUT= MAC=00:01:c0:0c:b0:a1:10:13:31:cb:27:48:08:00 SRC=194.147.140.25 DST=192.168.1.2 LEN=40 TOS=0x00 PREC=0x00 TTL=242 ID=24028 PROTO=TCP SPT=41873 DPT=54294 WINDOW=1024 RES=0x00 SYN URGP=0 
Jan 31 12:46:09 river kernel: [260744.333203] geo-filter DROP IN=enp2s0 OUT= MAC=00:01:c0:0c:b0:a1:10:13:31:cb:27:48:08:00 SRC=221.164.31.44 DST=192.168.1.2 LEN=40 TOS=0x00 PREC=0x00 TTL=49 ID=54844 PROTO=TCP SPT=28049 DPT=23 WINDOW=47224 RES=0x00 SYN URGP=0 
Jan 31 12:46:28 river kernel: [260763.664021] geo-filter DROP IN=enp2s0 OUT= MAC=00:01:c0:0c:b0:a1:10:13:31:cb:27:48:08:00 SRC=185.156.73.12 DST=192.168.1.2 LEN=40 TOS=0x00 PREC=0x00 TTL=180 ID=51557 PROTO=TCP SPT=57520 DPT=33443 WINDOW=1024 RES=0x00 SYN URGP=0 
```

* with parsed timestamps:

```bash
$ grep 'geo-filter DROP' /var/log/syslog | \
  tail -n5 | \
  ./ngf-parse-log.py --config=config.yaml --tz='Europe/Rome' 
2021-01-31T12:44:03+01:00 194.147.140.24 GB
2021-01-31T12:44:31+01:00 194.147.140.21 GB
2021-01-31T12:45:40+01:00 194.147.140.25 GB
2021-01-31T12:46:09+01:00 221.164.31.44 KR
2021-01-31T12:46:28+01:00 185.156.73.12 NL
```
