# Fitness App — Language Data That Must Not Be Mechanically Translated

**Inventory origin:** `xLZDx/Fitness-App`, default branch `master`, inspected Git tree. This companion to [Fitness-App document queue](Fitness-App.md) classifies the twelve filename matches that were **excluded** from documentation translation.

## Structured localization and source data (3)

| File | Classification | Rule |
| --- | --- | --- |
| `mobile/lib/l10n/app_ru.arb` | Deliberate Russian application locale | **Keep**. A localized customer interface is not an English-language GitHub documentation violation. Ensure English locale parity separately; do not overwrite the Russian locale or mutate localization keys. |
| `mobile/assets/data/equipment.ru.json` | Source-language-specific equipment data | Keep structured keys and native text until an approved locale-data mapping is verified. Translate explanations or add an English companion, not the source in place. |
| `mobile/assets/data/exercises_vendor.ru.json` | Russian vendor exercise catalog, approximately 3.2 MB | Do not run blanket translation or rename vendor IDs. It may be required for exercise lookup and provenance; review a dedicated English translation/mapping pipeline separately. |

## Binary exercise media (9)

```text
mobile/assets/posters/girl/ea_landmine_russian_twist.jpg
mobile/assets/posters/girl/ea_plate_russian_twist.jpg
mobile/assets/posters/men/ea_dumbbell_russian_twist_with_legs_floor_off.jpg
mobile/assets/posters/men/ea_dumbbell_straight_leg_russian_twist.jpg
mobile/assets/posters/men/ea_landmine_russian_twist.jpg
mobile/assets/posters/men/ea_plate_russian_twist.jpg
mobile/assets/posters/men/ea_russian_twist.jpg
mobile/assets/posters/men/ea_russian_twist_weighted_ball.jpg
mobile/assets/posters/men/fedb_russian_twist.jpg
```

Here, **Russian twist is the English name of an exercise**, not a Russian-language documentation fragment. These are binary assets and must not be renamed in a documentation-only PR; app source references may depend on their names.

**Conclusion:** Of 100 filename-pattern matches in Fitness-App, **88 are candidate document files** listed in `Fitness-App.md`, and these 12 are a distinct locale/data/media class. Do not count the 12 as untranslated GitHub comments, and do not falsely claim their replacement would improve English-only engineering documentation.
