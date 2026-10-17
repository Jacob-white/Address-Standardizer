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

/// Computes true Damerau-Levenshtein edit distance between s1 and s2.
/// Matches Python implementation in `address_standardizer.fuzzy._pure_damerau_levenshtein_distance`.
pub fn damerau_levenshtein(s1: &str, s2: &str) -> usize {
    if s1 == s2 {
        return 0;
    }
    let chars1: Vec<char> = s1.chars().collect();
    let chars2: Vec<char> = s2.chars().collect();
    let len1 = chars1.len();
    let len2 = chars2.len();
    if len1 == 0 {
        return len2;
    }
    if len2 == 0 {
        return len1;
    }

    let inf = len1 + len2;
    let mut da: std::collections::HashMap<char, usize> = std::collections::HashMap::new();
    let mut h = vec![vec![0usize; len2 + 2]; len1 + 2];

    h[0][0] = inf;
    for i in 0..=len1 {
        h[i + 1][0] = inf;
        h[i + 1][1] = i;
    }
    for j in 0..=len2 {
        h[0][j + 1] = inf;
        h[1][j + 1] = j;
    }

    for i in 1..=len1 {
        let mut db = 0;
        for j in 1..=len2 {
            let i1 = *da.get(&chars2[j - 1]).unwrap_or(&0);
            let j1 = db;
            let cost = if chars1[i - 1] == chars2[j - 1] {
                db = j;
                0
            } else {
                1
            };

            let deletion = h[i][j + 1] + 1;
            let insertion = h[i + 1][j] + 1;
            let substitution = h[i][j] + cost;
            let transposition = h[i1][j1] + (i - i1 - 1) + 1 + (j - j1 - 1);

            h[i + 1][j + 1] = deletion.min(insertion).min(substitution).min(transposition);
        }
        da.insert(chars1[i - 1], i);
    }

    h[len1 + 1][len2 + 1]
}

#[pyfunction]
pub fn damerau_levenshtein_distance(s1: &str, s2: &str) -> usize {
    damerau_levenshtein(s1, s2)
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
    dict.set_item("native_functions", vec!["compute_soundex", "damerau_levenshtein_distance"])?;
    Ok(dict)
}

#[pymodule]
fn _address_standardizer_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_soundex, m)?)?;
    m.add_function(wrap_pyfunction!(damerau_levenshtein_distance, m)?)?;
    m.add_function(wrap_pyfunction!(get_engine_name, m)?)?;
    m.add_function(wrap_pyfunction!(is_native, m)?)?;
    m.add_function(wrap_pyfunction!(get_capabilities, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{damerau_levenshtein, soundex};

    #[test]
    fn test_damerau_levenshtein_vectors() {
        assert_eq!(damerau_levenshtein("", ""), 0);
        assert_eq!(damerau_levenshtein("a", ""), 1);
        assert_eq!(damerau_levenshtein("", "a"), 1);
        assert_eq!(damerau_levenshtein("CA", "ABC"), 2);
        assert_eq!(damerau_levenshtein("MAIN", "MANI"), 1);
        assert_eq!(damerau_levenshtein("STREET", "STEET"), 1);
        assert_eq!(damerau_levenshtein("AVENUE", "AVE"), 3);
        assert_eq!(damerau_levenshtein("straße", "strasse"), 2);
    }

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
