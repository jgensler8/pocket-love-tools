character_map = {
    0x01: " ",  # tile 257
    0x02: " ",  # tile 258
    0x03: " ",  # tile 259
    0x04: " ",  # tile 260
    0x05: " ",  # tile 261
    0x06: " ",  # tile 262
    0x07: " ",  # tile 263
    0x08: " ",  # tile 264
    0x09: "あ",  # tile 265
    0x0A: "い",  # tile 266
    0x0B: "う",  # tile 267
    0x0C: "え",  # tile 268
    0x0D: "お",  # tile 269
    0x0E: "か",  # tile 270
    0x0F: "き",  # tile 271
    0x10: "く",  # tile 272
    0x11: "け",  # tile 273
    0x12: "こ",  # tile 274
    0x13: "さ",  # tile 275
    0x14: "し",  # tile 276
    0x15: "す",  # tile 277
    0x16: "せ",  # tile 278
    0x17: "そ",  # tile 279
    0x18: "た",  # tile 280
    0x19: "ち",  # tile 281
    0x1A: "つ",  # tile 282
    0x1B: "て",  # tile 283
    0x1C: "と",  # tile 284
    0x1D: "な",  # tile 285
    0x1E: "に",  # tile 286
    0x1F: "ぬ",  # tile 287
    0x20: "ね",  # tile 288
    0x21: "の",  # tile 289
    0x22: "は",  # tile 290
    0x23: "ひ",  # tile 291
    0x24: "ふ",  # tile 292
    0x25: "へ",  # tile 293
    0x26: "ほ",  # tile 294
    0x27: "ま",  # tile 295
    0x28: "み",  # tile 296
    0x29: "む",  # tile 297
    0x2A: "め",  # tile 298
    0x2B: "も",  # tile 299
    0x2C: "や",  # tile 300
    0x2D: "ゆ",  # tile 301
    0x2E: "よ",  # tile 302
    0x2F: "ら",  # tile 303
    0x30: "り",  # tile 304
    0x31: "る",  # tile 305
    0x32: "れ",  # tile 306
    0x33: "ろ",  # tile 307
    0x34: "わ",  # tile 308
    0x35: "を",  # tile 309
    0x36: "ん",  # tile 310
    0x37: "、",  # tile 311 , comma
    0x38: "。",  # tile 312 , period
    0x39: "ゃ",  # tile 313
    0x3A: "ゅ",  # tile 314
    0x3B: "ょ",  # tile 315
    0x3C: "っ",  # tile 316 , small
    0x3D: "ぁ",  # tile 317
    0x3E: "ぃ",  # tile 318
    0x3F: "ぅ",  # tile 319
    0x40: "ぇ",  # tile 320
    0x41: "ぉ",  # tile 321
    # potential "tick" start
    0x42: "が",  # tile 322
    0x43: "ぎ",  # tile 323
    0x44: "ぐ",  # tile 324 , voiced ku
    0x45: "げ",  # tile 325 , voiced ke
    0x46: "ご",  # tile 326
    0x47: "ざ",  # tile 327 , voiced sa
    0x48: "じ",  # tile 328 , voice shi
    0x49: "ず",  # tile 329 , voiced su
    0x4A: "ぜ",  # tile 330 , voiced se
    0x4B: "ぞ",  # tile 331 , unvoiced so
    0x4C: "だ",  # tile 332
    0x4D: "ぢ",  # tile 333
    0x4E: "づ",  # tile 334
    0x4F: "で",  # tile 335
    0x50: "ど",  # tile 336
    0x51: "ば",  # tile 337
    0x52: "び",  # tile 338
    0x53: "ぶ",  # tile 339
    0x54: "べ",  # tile 340
    0x55: "ぼ",  # tile 341
    0x56: "ぱ",  # tile 342
    0x57: "ぴ",  # tile 343
    0x58: "ぷ",  # tile 344
    0x59: "ぺ",  # tile 345
    0x5A: "ぽ",  # tile 346
    0x5B: "セ",  # tile 347 , katakana
    0x5C: "ン",  # tile 348 , katakana
    0x5D: "ス",  # tile 349 , katakana
    0x5E: "月",  # tile 350
    0x5F: "火",  # tile 351
    0x60: "水",  # tile 352
    0x61: "木",  # tile 353
    0x62: "金",  # tile 354
    0x63: "土",  # tile 355
    0x64: "日",  # tile 356
    0x65: "(",  # tile 357
    0x66: ")",  # tile 358
    # 0x67: '<continue>', # tile 359
    # 0x68: '<cursor>',   # tile 360
    # 0x69: '<heart>',    # tile 361
    0x67: "",  # tile 359
    0x68: "",  # tile 360
    0x69: "<3",  # tile 361
    0x6A: "!",  # tile 362
    0x6B: "?",  # tile 363
    0x6C: "A",  # tile 364
    0x6D: "B",  # tile 365
    0x6E: "=",  # tile 366
    0x6F: "0",  # tile 367
    0x70: "1",  # tile 368
    0x71: "2",  # tile 369
    0x72: "3",  # tile 370
    0x73: "4",  # tile 371
    0x74: "5",  # tile 372
    0x75: "6",  # tile 373
    0x76: "7",  # tile 374
    0x77: "8",  # tile 375
    0x78: "9",  # tile 376
    0x79: "day",  # tile 377
    0x7A: "~",  # tile 378
    0x7B: "-",  # tile 379
    0x7C: ".",  # tile 380
    0x7D: "/",  # tile 381
    0x7E: " ",  # tile 382
    0x7F: " ",  # tile 383 (designated space)
    0x80: " ",  # tile 384
    0x81: " ",  # tile 385 might be scene control char
    0x82: " ",  # tile 386 might be scene control char
    0xFE: " ",
}
