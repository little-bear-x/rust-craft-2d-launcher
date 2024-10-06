use std::process::Command;

slint::include_modules!();

fn main() -> Result<(), slint::PlatformError> {
    let main_window = MainWindow::new()?;
    let weak=main_window.as_weak();
    // 判断客户端类型
    let res = weak.upgrade().unwrap();
    if cfg!(target_os = "windows") {
        res.set_ua(slint::SharedString::from("Windows"));
    } else {
        res.set_ua(slint::SharedString::from("Unix"));
    }
    main_window.on_new_game(move || {
        let res=weak.upgrade().unwrap();
        let game_mode = res.get_game_mode().to_string();
        if game_mode == "经不了一典64方块"{
            let output = if cfg!(target_os = "windows") { 
                Command::new("./bin/rust-craft-2d.exe").output().expect("游戏启动异常")
            } else {
                Command::new("./bin/rust-craft-2d").output().expect("游戏启动异常")
            };
            let log = String::from_utf8(output.stdout);
            
            println!("{:?}", log.clone().unwrap());
            let shared_string_log = slint::SharedString::from(log.unwrap());
            res.set_log(shared_string_log);
        } else {
            let output = if cfg!(target_os = "windows") {
                Command::new("./bin/rust-craft-2d.exe").arg("--creative").output().expect("游戏启动异常")
            } else {
                Command::new("./bin/rust-craft-2d").arg("--creative").output().expect("游戏启动异常")
            };
            let log = String::from_utf8(output.stdout);
            
            println!("{:?}", log.clone().unwrap());
            let shared_string_log = slint::SharedString::from(log.unwrap());
            res.set_log(shared_string_log);
        }
        
    });
    main_window.run()
}
