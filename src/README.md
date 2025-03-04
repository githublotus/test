## RCB Installation Guide

### Step 1: Configure rcb.conf files

### Step 2:
```bash
touch rcb_daily_scan.log
```

### Step 3:
```bash
screen -dmS RCB_DL sh -c "rcb_daily_scan.sh"
```

### Step 4: Open ~/.bashrc to create aliases for "rm" and "rcb" commands
```bash
alias rm='python3 /root/test/src/rcb.py delete '
alias rcb='python3 /root/test/src/rcb.py '
```