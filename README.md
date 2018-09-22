# Bluetooth_DTW

terminalで以下のコマンドを実行.  
または，~/.bash_profileに書き込む  
`export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES`

送信  
センサ値送信  
`fprintf(bt, "%d\n", センサ値);`  
終端文字送信  
`fprintf(bt, "%c\n", '.');`
