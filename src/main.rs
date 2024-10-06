use std::process::Command;

slint::include_modules!();

fn main() -> Result<(), slint::PlatformError> {
    let main_window = MainWindow::new()?;
    let weak=main_window.as_weak();
    main_window.on_new_game(move || {
        let output = Command::new("./bin/rust-craft-2d").output().expect("游戏启动异常");
        let log = String::from_utf8(output.stdout);
        let res=weak.upgrade().unwrap();
        println!("{:?}", log.clone().unwrap());
        let shared_string_log = slint::SharedString::from(log.unwrap());
        res.set_log(shared_string_log);
    });
    main_window.run()
}