//! Native acceleration module for the Address Standardizer.
//!
//! The module deliberately exposes only functions whose behaviour is fully specified by the Python reference
//! implementation and checked against it by `tests/native/test_native_parity.py`. Everything else (parsing,
//! suffix/directional tables, key assembly) lives in Python, which is the single source of truth: earlier
//! Rust re-implementations of those rules drifted from the Python tables and produced different keys depending on
//! whether the extension happened to be installed.

use pyo3::prelude::*;
use pyo3::types::PyDict;

const VERSION: &str = env!("CARGO_PKG_VERSION");

#[inline]
fn soundex_code(c: char) -> char {
    match c {
        'B' | 'F' | 'P' | 'V' => '1',
        'C' | 'G' | 'J' | 'K' | 'Q' | 'S' | 'X' | 'Z' => '2',
        'D' | 'T' => '3',
        'L' => '4',
        'M' | 'N' => '5',
        'R' => '6',
        _ => '0',
    }
}

/// American Soundex of `token`, identical to `address_standardizer.phonetics._pure_compute_soundex`.
///
/// Python upper-cases with full Unicode rules (`"ß".upper() == "SS"`) and then drops everything outside `A-Z`;
/// `str::to_uppercase` applies the same expansions, so the two agree on non-ASCII input as well.
pub fn soundex(token: &str) -> String {
    let clean: Vec<char> = token
        .to_uppercase()
        .chars()
        .filter(|c| c.is_ascii_uppercase())
        .collect();

    let Some(&first) = clean.first() else {
        return String::new();
    };

    let mut code = String::with_capacity(4);
    code.push(first);
    let mut prev_code = soundex_code(first);

    for &c in &clean[1..] {
        let curr = soundex_code(c);
        if curr != '0' {
            if curr != prev_code {
                code.push(curr);
                if code.len() == 4 {
                    break;
                }
            }
            prev_code = curr;
        } else if matches!(c, 'A' | 'E' | 'I' | 'O' | 'U' | 'Y') {
            prev_code = '0';
        }
        // H and W do not reset prev_code (American Soundex)
    }

    while code.len() < 4 {
        code.push('0');
    }
    code
}

/// Computes the American Soundex code for a word token.
#[pyfunction]
pub fn compute_soundex(token: &str) -> String {
    soundex(token)
}

#[pyfunction]
pub fn get_engine_name() -> &'static str {
    "Rust_PyO3"
}

#[pyfunction]
pub fn is_native() -> bool {
    true
}

/// Describes what the native module really provides.
#[pyfunction]
pub fn get_capabilities(py: Python<'_>) -> PyResult<Bound<'_, PyDict>> {
    let dict = PyDict::new(py);
    dict.set_item("engine", "Rust_PyO3")?;
    dict.set_item("is_native", true)?;
    dict.set_item("version", VERSION)?;
    dict.set_item("pure_python", false)?;
    dict.set_item("native_functions", vec!["compute_soundex"])?;
    Ok(dict)
}

#[pymodule]
fn _address_standardizer_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_soundex, m)?)?;
    m.add_function(wrap_pyfunction!(get_engine_name, m)?)?;
    m.add_function(wrap_pyfunction!(is_native, m)?)?;
    m.add_function(wrap_pyfunction!(get_capabilities, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::soundex;

    #[test]
    fn classic_vectors() {
        assert_eq!(soundex("Robert"), "R163");
        assert_eq!(soundex("Rupert"), "R163");
        assert_eq!(soundex("Rubin"), "R150");
        assert_eq!(soundex("Ashcraft"), "A261");
        assert_eq!(soundex("Tymczak"), "T522");
        assert_eq!(soundex("Pfister"), "P236");
        assert_eq!(soundex("MAIN"), "M500");
    }

    #[test]
    fn empty_and_non_letters() {
        assert_eq!(soundex(""), "");
        assert_eq!(soundex("1234"), "");
        assert_eq!(soundex("  - "), "");
    }

    #[test]
    fn unicode_uppercasing_matches_python() {
        // Python: "straße".upper() == "STRASSE" -> S362
        assert_eq!(soundex("straße"), "S362");
        // "ﬁnch".upper() == "FINCH" (ligature expands) -> F520
        assert_eq!(soundex("ﬁnch"), "F520");
        // "ı".upper() == "I"
        assert_eq!(soundex("ıstanbul"), "I235");
    }

    #[test]
    fn never_panics_on_multibyte_input() {
        for s in ["ÄÖÜ", "日本語", "😀😀", "Ünïcödé", "ǅ"] {
            let _ = soundex(s);
        }
    }
}
