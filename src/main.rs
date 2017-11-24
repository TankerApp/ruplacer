extern crate clap;
extern crate ignore;
extern crate regex;
extern crate difference;
extern crate term;
extern crate structopt;

#[macro_use]
extern crate structopt_derive;



use structopt::StructOpt;
use ignore::Walk;
use std::path::Path;
use std::fs::File;
use std::io::prelude::*;
use regex::Regex;
use difference::{Changeset, Difference};

#[allow(unused_must_use)]
fn term_show_diff(before: &str, after: &str) {
   // Compare both texts, the third parameter defines the split level.
    let Changeset { diffs, .. } = Changeset::new(before, after, "\n");

    let mut t = term::stdout().unwrap();

    for i in 0..diffs.len() {
        match diffs[i] {
            Difference::Same(ref _x) => {
                t.reset().unwrap();
                writeln!(t, "");
            }
            Difference::Add(ref x) => {
                t.fg(term::color::GREEN).unwrap();
                writeln!(t, "+{}", x);
            }
            Difference::Rem(ref x) => {
                t.fg(term::color::RED).unwrap();
                writeln!(t, "-{}", x);
            }
        }
    }
    t.reset().unwrap();
    t.flush().unwrap();
}


pub struct Replacer {
    re: Regex,
    replacement: String,
}

impl Replacer {
    pub fn new(pattern: &str, replacement: &str) -> Replacer {
        let re = Regex::new(pattern).expect("Invalid regular expression");
        Replacer {
            re: re,
            replacement: replacement.to_string(),
        }
    }

    pub fn replace(&self, buf: &str) {
        let after = self.re.replace_all(buf, self.replacement.as_str());

        if buf != after {
            term_show_diff(buf, &after)
        }
        // let re = Regex::new(r"^\d{4}-\d{2}-\d{2}$").unwrap();

        // for m in greper.iter(data.as_bytes()) {
        //     println!("match: {} - {}", m.start(), m.end())
        // }
    }
}


fn grep_file(replacer: &Replacer, file_name: &Path) {
    if !file_name.is_file() {
        return
    }
    println!("{}", file_name.display());

    let mut f = File::open(file_name).expect("file not found");
    let mut data = String::new();
    f.read_to_string(&mut data).expect("error reading file");
    replacer.replace(data.as_str());

#[derive(StructOpt, Debug)]
#[structopt(name = "fr",
            version = "0.1.0",
            author = "The ruplacer team",
            about = "Find and Ruplace patterns in files and filenames.")]
struct Opt {
    #[structopt(short = "v", long = "verbose", help = "Activate verbose mode")]
    debug: bool,

    #[structopt(help = "The pattern to grep for")]
    pattern: String,

    #[structopt(help = "The replacement")]
    replacement: Option<String>,

    #[structopt(help = "paths (default to current working directory)")]
    paths: Vec<String>,
}

fn main() {
    let opts = Opt::from_args();
    let dirs: Vec<_> = match opts.paths.len() {
        0 => vec!["./".to_string()],
        _ => opts.paths,
    };

    let replacer = Replacer::new(opts.pattern.as_str(), opts.replacement);

    for dir in dirs {
        println!("Root directory: {}", dir);
        for result in Walk::new(dir) {
            // Each item yielded by the iterator is either a directory entry or an
            // error, so either print the path or the error.
            match result {
                Ok(entry) => replace_file(&replacer, entry.path()),
                Err(err) => println!("ERROR: {}", err),
            }
        }
    }
}
