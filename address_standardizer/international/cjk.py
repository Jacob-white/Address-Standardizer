"""East Asian / CJK Address Grammar (Japan, China, South Korea, Taiwan).

Provides specialized parsing and normalization for:
- Japan (JPN): Prefectures (都道府県), municipalities (市区町村), chome-ban-go (丁目-番-号),
  building/room (ビル, 号室), Kanji/Kana and Romanized.
- China (CHN): Provinces (省/自治区), municipal districts (市/区/县), roads (路/街/道),
  house numbers (号), rooms (室), Hanzi and Pinyin.
- South Korea (KOR): Road Name Address (ro/gil + building number), dong/gu hierarchy,
  Hangul and Romanized.
- Taiwan (TWN): Counties/cities (縣/市), districts (區/鄉/鎮), roads (路/街), sections (段),
  lanes (巷), alleys (弄), numbers (號), floors (樓).
"""

from __future__ import annotations

import re
from typing import ClassVar, List, Optional, Tuple

from address_standardizer._patterns import RE_COMMA_DOT, RE_WHITESPACE
from address_standardizer.international.base import (
    CountryGrammar,
    ParsedAddressComponents,
    split_intl_secondary_unit,
)
from address_standardizer.international.diacritics import (
    normalize_to_canonical_unicode,
)

# Japanese 47 Prefectures
JP_PREFECTURES = (
    "東京都", "北海道", "大阪府", "京都府",
    "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
    "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県",
    "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県",
    "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県",
)

# Korean Provinces and Metropolitan Cities
KR_PROVINCES = (
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시",
    "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원특별자치도", "강원도",
    "충청북도", "충청남도", "전라북도", "전북특별자치도", "전라남도",
    "경상북도", "경상남도", "제주특별자치도", "제주도",
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종", "경기", "강원",
)

# Taiwan Special Municipalities and Counties
TW_DIVISIONS = (
    "台北市", "臺北市", "新北市", "桃園市", "台中市", "臺中市",
    "台南市", "臺南市", "高雄市", "基隆市", "新竹市", "嘉義市",
    "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
    "屏東縣", "宜蘭縣", "花蓮縣", "台東縣", "臺東縣", "澎湖縣", "金門縣", "連江縣",
)

# Chinese Municipalities (Direct-controlled)
CN_DIRECT_MUNICIPALITIES = ("北京市", "上海市", "天津市", "重庆市", "北京", "上海", "天津", "重庆")

# Postal code patterns
RE_JP_POSTAL = re.compile(r"^(?:〒|\b)?([0-9]{3})-?([0-9]{4})\b")
RE_CN_POSTAL = re.compile(r"^\b([0-9]{6})\b")
RE_KR_POSTAL = re.compile(r"^\b([0-9]{5}|[0-9]{3}-[0-9]{3})\b")
RE_TW_POSTAL = re.compile(r"^\b([0-9]{3}(?:-?[0-9]{2,3})?)\b")

# Unit/Room indicators with non-overlapping patterns
RE_JP_ROOM = re.compile(r"(\d+(?:[\s\-]+)?(?:号室|室|階室|階|FL?\b))", re.IGNORECASE)
RE_CN_ROOM = re.compile(r"(\d+(?:[\s\-]+)?(?:室|层|楼|单元|号房))", re.IGNORECASE)
RE_KR_ROOM = re.compile(r"(\d+(?:[\s\-]+)?(?:호|층|동))", re.IGNORECASE)
RE_TW_ROOM = re.compile(r"(\d+(?:[\s\-]+)?(?:樓|楼|室|F\b))", re.IGNORECASE)

# Latin/Romanized Unit indicators
RE_LATIN_UNIT = re.compile(
    r"(?:\b(?:Apt|Suite|Ste|Unit|Room|Rm|Floor|Fl)\b|\b#)\.?\s*([A-Za-z0-9\-]+)\b",
    re.IGNORECASE,
)

_JP_ROOM_CHARS = ("号室", "室", "階", "階室", "F", "FL", "f", "fl")
_CN_ROOM_CHARS = ("室", "层", "楼", "单元", "号房")
_KR_ROOM_CHARS = ("호", "층", "동")
_TW_ROOM_CHARS = ("樓", "楼", "室", "F", "f")


def _search_cjk_room(text: str) -> Optional[re.Match]:
    """Search for CJK room/unit indicators with length capping and fast-path pre-check."""
    if not text:
        return None
    # Cap search length to prevent polynomial blowup on pathological payloads
    slice_text = text[:500]
    if any(k in slice_text for k in _JP_ROOM_CHARS):
        m = RE_JP_ROOM.search(slice_text)
        if m:
            return m
    if any(k in slice_text for k in _CN_ROOM_CHARS):
        m = RE_CN_ROOM.search(slice_text)
        if m:
            return m
    if any(k in slice_text for k in _KR_ROOM_CHARS):
        m = RE_KR_ROOM.search(slice_text)
        if m:
            return m
    if any(k in slice_text for k in _TW_ROOM_CHARS):
        m = RE_TW_ROOM.search(slice_text)
        if m:
            return m
    return RE_LATIN_UNIT.search(slice_text)


def _is_cjk(text: str) -> bool:
    """Check if string contains CJK ideographs, Hiragana, Katakana, or Hangul."""
    for ch in text:
        cp = ord(ch)
        if (
            0x4E00 <= cp <= 0x9FFF
            or 0x3400 <= cp <= 0x4DBF
            or 0x3040 <= cp <= 0x309F
            or 0x30A0 <= cp <= 0x30FF
            or 0xAC00 <= cp <= 0xD7AF
            or 0x1100 <= cp <= 0x11FF
        ):
            return True
    return False


class CJKGrammar(CountryGrammar):
    """Regional grammar family for East Asia (JPN, CHN, KOR, TWN)."""

    country_iso3: ClassVar[str] = "JPN"
    supported_countries: ClassVar[Tuple[str, ...]] = (
        "JPN", "JAPAN", "JP", "NIHON", "NIPPON",
        "CHN", "CHINA", "CN", "ZHONGGUO",
        "KOR", "SOUTH KOREA", "KOREA", "KR", "DAEHAN MINGUK", "REPUBLIC OF KOREA",
        "TWN", "TAIWAN", "TW", "ROC",
    )

    def normalize_postal_code(self, raw_code: str) -> str:
        """Normalize CJK postal code."""
        if not raw_code:
            return ""
        clean = " ".join(raw_code.strip().replace("〒", "").split())
        # Convert full-width digits if present
        trans = str.maketrans("０１２３４５６７８９", "0123456789")
        clean = clean.translate(trans)

        # Japan: 7 digits -> XXX-XXXX
        m_jp = re.match(r"^(\d{3})-?(\d{4})$", clean)
        if m_jp:
            return f"{m_jp.group(1)}-{m_jp.group(2)}"

        # China: 6 digits (continuous digits)
        m_cn = re.match(r"^(\d{6})$", clean)
        if m_cn:
            return m_cn.group(1)

        # South Korea: 5 digits (current) or legacy 6 digits (XXX-XXX with hyphen)
        m_kr = re.match(r"^(\d{5})$", clean)
        if m_kr:
            return m_kr.group(1)
        m_kr_old = re.match(r"^(\d{3})-(\d{3})$", clean)
        if m_kr_old:
            return f"{m_kr_old.group(1)}-{m_kr_old.group(2)}"

        # Taiwan: 3 to 6 digits
        m_tw = re.match(r"^(\d{3})(?:-?(\d{2,3}))?$", clean)
        if m_tw:
            return f"{m_tw.group(1)}-{m_tw.group(2)}" if m_tw.group(2) else m_tw.group(1)

        return clean

    def extract_premise_and_thoroughfare(
        self, street_line: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Extract (premise, street_number, thoroughfare) from CJK address line."""
        if not street_line:
            return None, None, None

        line = street_line.strip()
        line_slice = line[:500]

        # Romanized number-first: "6-10-1 Roppongi" or "152 Teheran-ro" or "No. 100 West Nanjing Road"
        m_rom_num = re.match(r"^(?:No\.?\s*)?(\d+[A-Za-z0-9\-\/]*)\s*,\s*(.*)$", line_slice, re.IGNORECASE)
        if not m_rom_num:
            m_rom_num = re.match(r"^(?:No\.?\s*)?(\d+[A-Za-z0-9\-\/]*)\s+([A-Za-zÀ-ÿ].*)$", line_slice, re.IGNORECASE)
        if m_rom_num:
            st_num = m_rom_num.group(1).strip()
            thoroughfare = m_rom_num.group(2).strip(" ,.")
            return None, st_num, f"{st_num} {thoroughfare}"

        # Native CJK thoroughfare with trailing number:
        # e.g. "霞が関1-1-1", "南京西路100号", "세종대로 110", "信義路五段7號"
        # Non-overlapping atomic pattern avoids polynomial backtracking on unbroken digit strings
        m_cjk_num = re.search(r"(\d+(?:[\-\/]\d+)*(?:号|號)?)\s*$", line_slice)
        if m_cjk_num:
            st_num = m_cjk_num.group(1).strip()
            return None, st_num, line

        return None, None, line

    def _resolve_iso3(self, country_cand: Optional[str]) -> str:
        """Resolve specific CJK country ISO-3."""
        if not country_cand:
            return "JPN"
        c = country_cand.strip().upper()
        if c in ("JPN", "JAPAN", "JP", "NIHON", "NIPPON"):
            return "JPN"
        if c in ("CHN", "CHINA", "CN", "ZHONGGUO"):
            return "CHN"
        if c in ("KOR", "SOUTH KOREA", "KOREA", "KR", "DAEHAN MINGUK", "REPUBLIC OF KOREA"):
            return "KOR"
        if c in ("TWN", "TAIWAN", "TW", "ROC"):
            return "TWN"
        return "JPN"

    def parse(self, raw_tokens: List[str], metadata: dict) -> ParsedAddressComponents:
        s1_raw = metadata.get("street1", "")
        s2_raw = metadata.get("street2", "")
        city_raw = metadata.get("city", "")
        state_raw = metadata.get("state", "")
        postal_raw = metadata.get("postal_code", "")
        country_raw = metadata.get("country", self.country_iso3)
        country_iso = self._resolve_iso3(country_raw)

        unit_type: Optional[str] = None
        unit_number: Optional[str] = None
        building_name: Optional[str] = None
        dep_locality: Optional[str] = None
        street_line = s1_raw

        # -------------------------------------------------------------
        # 1. Comma-delimited Romanized single string parsing
        # -------------------------------------------------------------
        if not city_raw and s1_raw and "," in s1_raw:
            parts = [p.strip() for p in s1_raw.split(",") if p.strip()]
            # Strip trailing country if present
            if len(parts) >= 2 and parts[-1].upper() in self.supported_countries:
                country_iso = self._resolve_iso3(parts[-1])
                parts = parts[:-1]

            # Extract postal code from rightmost token if present (e.g. "Tokyo 106-6132" or "Seoul 06236" or "Taipei City 110")
            if len(parts) >= 2:
                last_p = parts[-1]
                m_pc = re.search(r"\b(\d{3}-?\d{4}|\d{5,6}|\d{3}(?:-?\d{2,3})?)\b", last_p)
                if m_pc and not postal_raw:
                    postal_raw = m_pc.group(1)
                    clean_loc = last_p[:m_pc.start()] + last_p[m_pc.end():]
                    parts[-1] = clean_loc.strip()

            if len(parts) >= 3:
                # e.g. ["Roppongi Hills Mori Tower 32F", "6-10-1 Roppongi", "Minato-ku", "Tokyo"]
                # OR ["No. 7", "Sec. 5", "Xinyi Rd.", "Xinyi Dist.", "Taipei City"]
                state_raw = parts[-1]
                city_raw = parts[-2]
                rem_parts = parts[:-2]
                if len(rem_parts) == 1:
                    street_line = rem_parts[0]
                else:  # two or more leading parts (rem_parts is never empty when len(parts) >= 3)
                    if re.match(r"^(?:No\.?\s*)?\d", rem_parts[0], re.IGNORECASE):
                        street_line = ", ".join(rem_parts)
                    else:
                        building_name = rem_parts[0]
                        street_line = ", ".join(rem_parts[1:])
            elif len(parts) == 2:
                # e.g. ["6-10-1 Roppongi", "Tokyo"] (parts never contain commas: the line was split on them)
                city_raw = parts[1]
                street_line = parts[0]
            elif len(parts) == 1:
                street_line = parts[0]

        # -------------------------------------------------------------
        # 2. Native CJK Unparsed Hierarchy Parsing
        # -------------------------------------------------------------
        elif not city_raw and s1_raw and _is_cjk(s1_raw):
            work = s1_raw.strip()

            # Extract postal code if present at start or end
            m_post = re.search(r"(?:〒|\b)(\d{3}-\d{4}|\d{5,6})\b", work)
            if m_post and not postal_raw:
                postal_raw = m_post.group(1)
                work = work[:m_post.start()] + work[m_post.end():]
                work = work.strip()

            # Separate whitespace-delimited tokens if present (e.g. "東京都港区六本木6-10-1 六本木ヒルズ森タワー 32階")
            w_tokens = work.split()
            main_block = w_tokens[0] if w_tokens else ""
            tail_tokens = w_tokens[1:] if len(w_tokens) > 1 else []

            # Check if address is split into whitespace-delimited administrative tokens
            # (Very common in Korean: "서울특별시 강남구 테헤란로 152", and also Chinese: "北京市 海淀区 中关村南大街1号")
            is_div_token = len(w_tokens[0]) <= 5 and (
                any(w_tokens[0] == p for p in KR_PROVINCES)
                or any(w_tokens[0] == p for p in JP_PREFECTURES)
                or any(w_tokens[0] == p for p in CN_DIRECT_MUNICIPALITIES)
                or any(w_tokens[0] == p for p in TW_DIVISIONS)
                or w_tokens[0].endswith(("省", "市", "道", "県", "府"))
            )
            if len(w_tokens) >= 3 and is_div_token:
                state_raw = w_tokens[0]
                city_raw = w_tokens[1]
                idx = 2
                if idx < len(w_tokens) and any(w_tokens[idx].endswith(s) for s in ("区", "區", "县", "縣", "군", "구")) and len(w_tokens) > 3:
                    dep_locality = w_tokens[idx]
                    idx += 1
                rem_tokens = w_tokens[idx:]

                # Scan rem_tokens for room / building
                street_tokens = []
                for token in rem_tokens:
                    m_rm = _search_cjk_room(token)
                    if m_rm and not unit_number:
                        unit_number = m_rm.group(1).strip()
                        rem_bldg = token[:m_rm.start()] + token[m_rm.end():]
                        if rem_bldg.strip() and not building_name:
                            building_name = rem_bldg.strip()
                    elif token.endswith(("빌딩", "타워", "센터", "大厦", "大楼", "中心", "ビル", "タワー")) and not building_name:
                        building_name = token.strip()
                    else:
                        street_tokens.append(token)
                street_line = " ".join(street_tokens)
                tail_tokens = []

            # 2A. Japan native hierarchy
            elif country_iso == "JPN" or any(main_block.startswith(p) for p in JP_PREFECTURES):
                country_iso = "JPN"
                for pref in JP_PREFECTURES:
                    if main_block.startswith(pref):
                        state_raw = pref
                        main_block = main_block[len(pref):]
                        break
                # Municipality: ends with 市, 区, 町, 村
                m_muni = re.match(r"^(.*?[市区町村郡])(.*)$", main_block)
                if m_muni:
                    city_raw = m_muni.group(1)
                    street_line = m_muni.group(2)
                else:
                    street_line = main_block

            # 2B. China native hierarchy
            elif country_iso == "CHN" or any(main_block.startswith(p) for p in CN_DIRECT_MUNICIPALITIES):
                country_iso = "CHN"
                for d_mun in CN_DIRECT_MUNICIPALITIES:
                    if main_block.startswith(d_mun):
                        state_raw = d_mun if d_mun.endswith("市") else f"{d_mun}市"
                        main_block = main_block[len(d_mun):]
                        break
                if not state_raw:
                    m_prov = re.match(r"^(.*?(?:省|自治区))(?=.*[市区县])", main_block)
                    if m_prov:
                        state_raw = m_prov.group(1)
                        main_block = main_block[len(state_raw):]

                m_cn_city = re.match(r"^(.*?[市区县旗])(.*)$", main_block)
                if m_cn_city:
                    city_raw = m_cn_city.group(1)
                    street_line = m_cn_city.group(2)
                else:
                    street_line = main_block

            # 2C. South Korea native hierarchy
            elif country_iso == "KOR" or any(main_block.startswith(p) for p in KR_PROVINCES):
                country_iso = "KOR"
                for kr_prov in KR_PROVINCES:
                    if main_block.startswith(kr_prov):
                        rest_block = main_block[len(kr_prov):].strip()
                        if rest_block.endswith(("로", "길")) and not re.search(r"[시군구]", rest_block):
                            # "세종대로": the province-like prefix is part of a road name, not a province.
                            break
                        state_raw = kr_prov
                        main_block = rest_block
                        break
                m_kr_city = re.match(r"^(.*?[시군구])\s*(.*)$", main_block)
                if m_kr_city:
                    city_raw = m_kr_city.group(1)
                    street_line = m_kr_city.group(2)
                else:
                    street_line = main_block

            # 2D. Taiwan native hierarchy
            else:  # country_iso is always one of JPN/CHN/KOR/TWN here, and the first three were handled above
                country_iso = "TWN"
                for tw_div in TW_DIVISIONS:
                    if main_block.startswith(tw_div):
                        state_raw = tw_div
                        main_block = main_block[len(tw_div):]
                        break
                m_tw_dist = re.match(r"^(.*?[區鄉鎮市])(.*)$", main_block)
                if m_tw_dist:
                    city_raw = m_tw_dist.group(1)
                    street_line = m_tw_dist.group(2)
                else:
                    street_line = main_block

            # Process tail tokens for building, room, or trailing postal code
            if tail_tokens:
                for token in tail_tokens:
                    # Korean road name (…로/…길) followed by a short number: that is the building number.
                    if (
                        country_iso == "KOR"
                        and street_line.endswith(("로", "길"))
                        and re.match(r"^\d{1,4}(?:-\d{1,4})?$", token.strip())
                    ):
                        street_line = f"{street_line} {token.strip()}"
                        continue
                    # Check for trailing postal code (e.g. "110", "106-6132", "06236")
                    if re.match(r"^\d{3}(?:-?\d{2,4})?$", token.strip()) and not postal_raw:
                        postal_raw = token.strip()
                        continue

                    m_rm = _search_cjk_room(token)
                    if m_rm and not unit_number:
                        unit_number = m_rm.group(1).strip()
                        rem_bldg = token[:m_rm.start()] + token[m_rm.end():]
                        if rem_bldg.strip() and not building_name:
                            building_name = rem_bldg.strip()
                    elif not building_name:
                        building_name = token.strip()

        # -------------------------------------------------------------
        # 3. Unit, Room & Building Extractions from street2 or street_line
        # -------------------------------------------------------------
        if s2_raw:
            m_s2_rm = _search_cjk_room(s2_raw)
            if m_s2_rm:
                unit_number = m_s2_rm.group(1).strip()
            else:
                unit_number = s2_raw.strip()

        # Check inline room in street_line
        m_inline_rm = _search_cjk_room(street_line)
        if m_inline_rm and not unit_number:
            unit_number = m_inline_rm.group(1).strip()
            street_line = street_line[:m_inline_rm.start()] + street_line[m_inline_rm.end():]
            street_line = RE_WHITESPACE.sub(" ", street_line.strip(" ,.-"))

        # Check secondary unit in Latin street line
        st1_base, st2_base = split_intl_secondary_unit(street_line, "")
        if st2_base and not unit_number:
            s2_p = st2_base.split(maxsplit=1)
            unit_type = s2_p[0]
            unit_number = s2_p[1] if len(s2_p) > 1 else None
            street_line = st1_base

        _, st_num, thoroughfare = self.extract_premise_and_thoroughfare(street_line)
        full_street = thoroughfare or street_line

        # Canonical normalization
        norm_postal = self.normalize_postal_code(postal_raw)
        norm_city = normalize_to_canonical_unicode(RE_COMMA_DOT.sub(" ", city_raw).strip())
        norm_state = normalize_to_canonical_unicode(RE_COMMA_DOT.sub(" ", state_raw).strip())
        norm_street = normalize_to_canonical_unicode(full_street.strip()) if full_street else None
        norm_bldg = normalize_to_canonical_unicode(building_name.strip()) if building_name else None

        # If native CJK and st_num is already in norm_street, don't duplicate
        if norm_street and st_num and _is_cjk(norm_street) and st_num in norm_street:
            st_num = None

        # Uppercase Romanized city/state if Latin script
        if norm_city and norm_city.isascii():
            norm_city = norm_city.upper()
        if norm_state and norm_state.isascii():
            norm_state = norm_state.upper()
        if norm_street and norm_street.isascii():
            norm_street = norm_street.upper()

        norm_st_num = st_num.upper() if st_num and st_num.isascii() else st_num

        return ParsedAddressComponents(
            street_number=norm_st_num,
            street_name=norm_street,
            unit_type=unit_type,
            unit_number=unit_number,
            building_name=norm_bldg,
            dependent_locality=dep_locality,
            city=norm_city if norm_city else None,
            state=norm_state if norm_state else None,
            postal_code=norm_postal if norm_postal else None,
            country_iso3=country_iso,
            raw_tokens=raw_tokens,
        )
