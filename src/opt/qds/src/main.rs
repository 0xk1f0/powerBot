use clap::Parser;
use image::{imageops::FilterType, GenericImageView};
use std::fs;
use std::path::{Path, PathBuf};
use std::process;

/// QuickDownScaler
#[derive(Parser, Debug)]
#[command(long_about = None)]
struct Args {
    /// Image File Path
    #[arg(short, long)]
    image: String,
}

pub struct Subject {
    pub image_path: PathBuf,
}

impl Subject {
    pub fn new() -> Result<Self, String> {
        // handle args
        let args = Args::parse();

        // check if path is valid
        if !fs::metadata(Path::new(&args.image)).is_ok() {
            Err("Invalid Image Path")?
        }

        // construct
        Ok(Self {
            image_path: Path::new(&args.image).to_path_buf(),
        })
    }

    pub fn downscale(self) -> Result<(), String> {
        // open the image
        let mut image = image::open(&self.image_path).map_err(|err| err.to_string())?;

        // check file name
        let file_name = &self
            .image_path
            .file_name()
            .unwrap()
            .to_string_lossy()
            .to_string();

        // set new filename
        let new_filename = format!(
            "qds_procd_{}",
            file_name,
        );

        // full image path
        let mut path_image = self.image_path.clone();
        path_image.set_file_name(new_filename);

        // check dimensions
        let (width, height) = image.dimensions();

        // check conditions
        if width > 800 && height > 800 {
            // calculate downscaled size
            let new_width = (width as f32 * 0.8).round();
            let new_heigth = (height as f32 * 0.8).round();

            // resize it
            image = image.resize(new_width as u32, new_heigth as u32, FilterType::Lanczos3);

            // save the image
            image.save(path_image).map_err(|err| err.to_string())?;
        } else {
            // image is small enough, just rename it as processed
            fs::rename(self.image_path, path_image).map_err(|err| err.to_string())?;
        }

        // return
        Ok(())
    }
}

fn run() -> Result<(), String> {
    // gen new config
    let config = Subject::new().map_err(|err| err.to_string())?;

    // downscale
    config.downscale().map_err(|err| err.to_string())?;

    // return
    Ok(())
}

fn main() {
    // run with config
    if let Err(err) = run() {
        eprintln!("{}: {}", "qds", err);
        process::exit(1);
    }
}
