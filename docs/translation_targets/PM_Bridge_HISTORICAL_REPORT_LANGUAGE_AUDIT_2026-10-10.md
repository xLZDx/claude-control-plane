# PM Bridge — Direct Audit of All 57 English Historical HTML Reports

**Date:** October 10, 2026  
**Repository:** [PM_Bridge](https://github.com/xLZDx/PM_Bridge)  
**Verified draft HEAD:** `9cee55d933688abd0726566202090d48e01b04fc`  
**Method:** Each English report matched to its original `.ru.html` at the pinned Git tree, fetched through its actual Git blob SHA, tested for literal Cyrillic and inspected for locally linked records. **No** past report was rewritten.

## Exact source-English blob audit (57 report pairs)

| Original Russian report | Original blob SHA | English report | English blob SHA | Cyrillic in English HTML |
| --- | --- | --- | --- | ---: |
| `reports/ACTIVEJOBS_WEDGE_CLOSED.ru.html` | `383a58a409dbc5c79559eddc5e06fe318be2c36a` | `reports/ACTIVEJOBS_WEDGE_CLOSED.html` | `68ed7359f85aecb60a74ebb4c4c7b806ca14e848` | 0 |
| `reports/AMBIGUOUS_LEASE_INCIDENT.ru.html` | `fccdf940b435d69d1c5d2fe1dbb13608e6aa30bd` | `reports/AMBIGUOUS_LEASE_INCIDENT.html` | `4fcdff1332c25fc37fef321ad3344f214bc9da79` | 0 |
| `reports/AUTO_REGISTRATION_CLOSED.ru.html` | `f91686beaad8976b806562cd53b5ec4513137694` | `reports/AUTO_REGISTRATION_CLOSED.html` | `437dfdff9e60a94ad627ef859a4ffaea4d10db76` | 0 |
| `reports/B1_RESOLUTION_AUTHORITY.ru.html` | `0633642002b200dc68ac995f8e356f9bae8f1d92` | `reports/B1_RESOLUTION_AUTHORITY.html` | `0e9598f9dbc683585fda54445c34ba10b1dc0af9` | 0 |
| `reports/B2_CALLER_CUTOVER.ru.html` | `a55bc8c35fd45e7a1ffb1ded6d30db3448a65cac` | `reports/B2_CALLER_CUTOVER.html` | `5404844ff246d57a192dee9dda971bb5204d2b11` | 0 |
| `reports/bridge-outage-fixes-2026-09-12.ru.html` | `559e531a2f7cc031316a887c9c901b078cbc95a8` | `reports/bridge-outage-fixes-2026-09-12.html` | `a702e30ba4979b9bae17e7af5d620e6831fb30a2` | 0 |
| `reports/CDP_TABS_SHUTDOWN_CLEANUP_GATE.ru.html` | `398a40ac081cfc69435e9e686209a9dcecc32aca` | `reports/CDP_TABS_SHUTDOWN_CLEANUP_GATE.html` | `5bc28689496639f6e0837fbf11822bbaef8c1457` | 0 |
| `reports/COMPOSER_CARD_MARKUP_GATE.ru.html` | `54ce36c772f7477155f29768d3692f1933378e4e` | `reports/COMPOSER_CARD_MARKUP_GATE.html` | `a2e5fc03b320458142da029dbc703458fa6bae13` | 0 |
| `reports/DAEMON_HARDENING_AND_5CLIENT_SIM.ru.html` | `f309bc67024438f1f013552bc5b506fd2661bd3b` | `reports/DAEMON_HARDENING_AND_5CLIENT_SIM.html` | `0319600f3846cf2ee7a83dbcc1d8969ed93ad237` | 0 |
| `reports/DEPLOY_COMPLETION_BRANCH_MERGE.ru.html` | `8ddd1e7b6a42a53bd678708f2d236d5f79ca7740` | `reports/DEPLOY_COMPLETION_BRANCH_MERGE.html` | `0808225a37b4f118616309e080b44cc88d0cf7c9` | 0 |
| `reports/e2e-concurrency-verification-2026-09-15.ru.html` | `864001d03655db4405a3a9c8e7d9603d8d9995eb` | `reports/e2e-concurrency-verification-2026-09-15.html` | `10e69889f722a0e47faecd9eb74d0de8ffcbaa9e` | 0 |
| `reports/FAILED_TO_LOAD_RECOVERY.ru.html` | `cb6eb8feeb42bb05440542d3d0a45a3dba109177` | `reports/FAILED_TO_LOAD_RECOVERY.html` | `406f29998e4565a9299656382edd2430fe81be88` | 0 |
| `reports/FILE_ATTACHMENTS_GATE.ru.html` | `944b69b698632a4ca7f86927ea2d980004c500bd` | `reports/FILE_ATTACHMENTS_GATE.html` | `da54ed516a4dadde2366c09948519641c5f10088` | 0 |
| `reports/FINGERPRINT_OPERATOR_GATE.ru.html` | `c549dc2b496ccf5ce59737d44918e678c796efff` | `reports/FINGERPRINT_OPERATOR_GATE.html` | `fc3d189799d1631b16f0659726576936ffb15bbc` | 0 |
| `reports/GATE_5_CLOSURE.ru.html` | `db467915c001af98bb87021cf6b8cdb86bd5cde3` | `reports/GATE_5_CLOSURE.html` | `e369f6825302eb8f414231f5cbcaaef46677e011` | 0 |
| `reports/GATE_C1_HOOKS_CLOSED.ru.html` | `42de2a24e20f18e920c945a5a13fd6fc21e0794b` | `reports/GATE_C1_HOOKS_CLOSED.html` | `41e82b7881d22710556875db04e440a51551c0d1` | 0 |
| `reports/GATE_P_LIVE_PROBES.ru.html` | `5ffc928cea76f3e9ced86f674d69d443dbdeb412` | `reports/GATE_P_LIVE_PROBES.html` | `632d96c56a2fc75eb92c728c57c8530c93662499` | 0 |
| `reports/GATES_A_B1_B2_STATUS.ru.html` | `c8297a77769a6cf898fd90360cca06a66bbd00a4` | `reports/GATES_A_B1_B2_STATUS.html` | `66abbecf79cb2278029d8fceaf1c7b582c55528b` | 0 |
| `reports/GATES_AB2_INTERNAL_REVIEW.ru.html` | `29ecf8dc9e9f81d9f17f07a6dcfa632ff1d622eb` | `reports/GATES_AB2_INTERNAL_REVIEW.html` | `81de68a97ff33d43a634b2ddd6f1e53ae1c332d6` | 0 |
| `reports/HANDOFF_CONSOLIDATION.ru.html` | `79ba5fbcb1d9c788eb0ecdc4847f617445e7d580` | `reports/HANDOFF_CONSOLIDATION.html` | `4416ef5b679ae969b734e8aa187b1e93638def79` | 47 |
| `reports/HANDOFF_EXPORT_CDP_RECOVERY_GATE.ru.html` | `87bcac2854f515606045f434022892c28e89da15` | `reports/HANDOFF_EXPORT_CDP_RECOVERY_GATE.html` | `276d9377b9fda59ee77edc90e8b3fc14763e756b` | 0 |
| `reports/HARVEST_ARMING_RENAME_GATE.ru.html` | `216eeffb66556e226ee28a57531013ce9bb2ab52` | `reports/HARVEST_ARMING_RENAME_GATE.html` | `b19742081602f76bb05b2d0064a03dcb23f439be` | 0 |
| `reports/LIFECYCLE_DIVERGENCE_CLOSED.ru.html` | `c3fff2218949f8e8ca55fca6102efb7501a22a34` | `reports/LIFECYCLE_DIVERGENCE_CLOSED.html` | `224362394d57398b8ef8108188198a88cda6796c` | 209 |
| `reports/LIVE_E2E_AND_PRODUCTION_CUTOVER.ru.html` | `1fb8da344509ca730ba2a1ce517b129100297de5` | `reports/LIVE_E2E_AND_PRODUCTION_CUTOVER.html` | `86b30a2be76c1894a69bc793fc87e2a834c6839e` | 0 |
| `reports/NEW_PROJECT_CHAT_GATE.ru.html` | `aac13eb7463f5229d7cdaeb3f0c4543602951c8c` | `reports/NEW_PROJECT_CHAT_GATE.html` | `96f8ae7a36b1de008e0ce818ed40bcef492932aa` | 0 |
| `reports/NEW_PROJECT_REGISTER_GATE.ru.html` | `647684e692ca222c3e3811c669302cc59fcb7e12` | `reports/NEW_PROJECT_REGISTER_GATE.html` | `0206a5e6abeb795480dc10e5ed293b27522362de` | 0 |
| `reports/NO_RENAME_MAJOR_FIXES_GATE.ru.html` | `d0df067584a5bcc3eb914016d946e03c2a8c825f` | `reports/NO_RENAME_MAJOR_FIXES_GATE.html` | `c1c64005753f4fbbbc78a01c67a730bdce6ad9d5` | 0 |
| `reports/PM_BRIDGE_BUILDID_SKEW.ru.html` | `1e39d02e2cbf5ae8b31ac22f8ae1db1986dae6cd` | `reports/PM_BRIDGE_BUILDID_SKEW.html` | `aefcc5671471de6b8ed65f0ed79436c5f3d63d79` | 34 |
| `reports/PM_BRIDGE_COMPLETION_READY.ru.html` | `4778e8ee5421b8c6e190f72ddcf0592ccdeb82c4` | `reports/PM_BRIDGE_COMPLETION_READY.html` | `2d7a15e7e2ca6322978813aae7b9c3462efa0884` | 0 |
| `reports/PM_BRIDGE_CONCURRENCY_ROADMAP.ru.html` | `efe173e864737a38925a58d24c5df90c9c587988` | `reports/PM_BRIDGE_CONCURRENCY_ROADMAP.html` | `c0292de239701e2b548f08c63a9a5107c182f42f` | 0 |
| `reports/PM_BRIDGE_GATE_A_PASTE_FREEZE.ru.html` | `70990c67dbb1a0f990c0bdfcb5467f88970cc758` | `reports/PM_BRIDGE_GATE_A_PASTE_FREEZE.html` | `7028cbc056034f6c28f0bbb11ab81520aae1751e` | 0 |
| `reports/PM_BRIDGE_POLICY_LAYER.ru.html` | `b3815369bb719b2f374b56bd2ab6eef67c9b9ad3` | `reports/PM_BRIDGE_POLICY_LAYER.html` | `93592b492bb289f4aaded0acbef4946b98a03c8e` | 0 |
| `reports/PM_BRIDGE_SESSION_STOP_RULE.ru.html` | `fcd1c5c16a2aa981c8fd46d21afb515b30d6f223` | `reports/PM_BRIDGE_SESSION_STOP_RULE.html` | `090aa255ca8e8cb5633e55cd438e4bd53eb742da` | 0 |
| `reports/PM_BRIDGE_WATCH_CLOSED.ru.html` | `5b2d3636c7d9f097fdcabf3dc08809f45eb9cb7c` | `reports/PM_BRIDGE_WATCH_CLOSED.html` | `dc0aeb520e30b723fc8557ad7f4d072a7c491915` | 0 |
| `reports/pm-bridge-gate2-live-fix.ru.html` | `6996785dfd52d57ddb0b3f60c2448acf2f81b4d0` | `reports/pm-bridge-gate2-live-fix.html` | `7f6c9c86b28fb496ca1cd008ddb5d92df215d976` | 0 |
| `reports/pm-bridge-gate5.ru.html` | `e35191205d79b4992d6157d0b01c7b5fb4d8f704` | `reports/pm-bridge-gate5.html` | `8cfd94c8a8af0fad0771f3a46cb2405534e84efa` | 0 |
| `reports/pm-bridge-gates-1-4.ru.html` | `59cdf195db6496308e361cbb2ff2b4035789dad3` | `reports/pm-bridge-gates-1-4.html` | `072e277d4cab154c7e4ce1969c27d4ad102589e2` | 0 |
| `reports/pm-bridge-plan-approval-gate.ru.html` | `2bbf0d01c8dcf3ebf252040a1981e5b2a9b675ca` | `reports/pm-bridge-plan-approval-gate.html` | `b37d8dff2f36ae39dcf672c7d153e9fd9ddb5465` | 20 |
| `reports/pm-bridge-retrospective-2026-09-17.ru.html` | `c9d56b8f367f7674dfdcf79211c0b756eec43aea` | `reports/pm-bridge-retrospective-2026-09-17.html` | `7268aaf21daaff1974a3697036fc7e128ef70cc0` | 26 |
| `reports/PUSH_AND_MERGE_PLAN.ru.html` | `cdd6591c6b93569eb318eef653bf353e774237eb` | `reports/PUSH_AND_MERGE_PLAN.html` | `f3b038fc49de0e018796c2ff7e2944ddc1d700a0` | 0 |
| `reports/rate-limit-and-daemon-stability-2026-09-18.ru.html` | `31e4702003ca36e0dbf549795cc92616be93b35a` | `reports/rate-limit-and-daemon-stability-2026-09-18.html` | `f9d8c5b69a5497f132f1d53485a86adfbcef6ef0` | 0 |
| `reports/RENAME_RETRY_LEAK_GATE.ru.html` | `341c629fec5438fb9f664b9b8190c3b2c8ba2664` | `reports/RENAME_RETRY_LEAK_GATE.html` | `6865451099735e60713554c075ab31826c28f6db` | 0 |
| `reports/REPLY_COMPLETION_GATE.ru.html` | `dc5d10dc95f3c9dd5a591dd76f781390efb10a05` | `reports/REPLY_COMPLETION_GATE.html` | `c839036e91f07a779adf0f11ee0cfc4635e0fd87` | 0 |
| `reports/request-id-wire-protocol-2026-09-12.ru.html` | `f74c4f57601eb82a75bd8c45973bee28c30f49e1` | `reports/request-id-wire-protocol-2026-09-12.html` | `6ccb8b36dae3d6bd65ccb833d09065bd951d9f08` | 17 |
| `reports/ROSETTA_GOVERNANCE_ORPHANED_PLANS.ru.html` | `28bd686d5cd10a8d61fc1f3adff57e279d221abd` | `reports/ROSETTA_GOVERNANCE_ORPHANED_PLANS.html` | `4aa7038fe050d725cf5dbac725dc8353c72b15b5` | 0 |
| `reports/ROSETTA_R0.ru.html` | `b98a56a1a031948b981ea7f623e5c7dc2ee5094b` | `reports/ROSETTA_R0.html` | `d2520b49f895213984da802ef2fa02759dfe5974` | 0 |
| `reports/ROUTING_IDENTITY_GATE.ru.html` | `ed1646cf01001e9d65252ba5bbfa9e0561b7bb79` | `reports/ROUTING_IDENTITY_GATE.html` | `2383d9aa13834894f13d4af0685b97d388865d8d` | 0 |
| `reports/RUN_2026-08-29_FINAL.ru.html` | `cc02e5710d864db25696241b530452bb716e4257` | `reports/RUN_2026-08-29_FINAL.html` | `1891d40ee5aa258e183ad0c4964b9dfb287d8b7d` | 30 |
| `reports/security-review-closure-plan-2026-09-13.ru.html` | `000b5ef6403220fb5b79e8eb58a3528b74ae96e4` | `reports/security-review-closure-plan-2026-09-13.html` | `7119d939748b5d57722a9cc9b639ccb27f6b3349` | 0 |
| `reports/SOURCE_UPDATE_HANDOFF_FIXES.ru.html` | `a43800d5f527c85fc9088eef85d5886c0633e405` | `reports/SOURCE_UPDATE_HANDOFF_FIXES.html` | `99d600f701e72a6aad8cb482dc235f5376503df3` | 0 |
| `reports/START_TIMEOUT_FIX_CLOSED.ru.html` | `fc5ae5404a3505aac0ce657765ef29770c60f50c` | `reports/START_TIMEOUT_FIX_CLOSED.html` | `280415609935b7c4f2ec8ae18cd012634117d1bc` | 0 |
| `reports/STARTUP_RETRY_GATE.ru.html` | `edcc9bf86c703d916f7c440b71b603e1fc23f697` | `reports/STARTUP_RETRY_GATE.html` | `3a3760d0f1e31e201a8a5e85b2dd39be88ad4445` | 0 |
| `reports/T1A_CLOSED.ru.html` | `34960108c315e04923b93eead4a6457c99217090` | `reports/T1A_CLOSED.html` | `d0b7cdc5da382e29cfe4ab034d2fa12028c0d18a` | 0 |
| `reports/T1C_REVIEW_MAJOR_X6.ru.html` | `194954a0520921f24f26031dec2fb5c66b1d432e` | `reports/T1C_REVIEW_MAJOR_X6.html` | `fde2655eb2cdde31599ace9b63ad951810c81a90` | 0 |
| `reports/T1C_REVIEW.ru.html` | `0a8a2ef68a140df2d05963b75e753c03ff4bc438` | `reports/T1C_REVIEW.html` | `f62bd130f2c338d48c2b84058b0c507f2c2bc887` | 0 |
| `reports/UNCERTAIN_TERMINAL_STATUS.ru.html` | `d670368a314dcad0082bb2fb485711bb5f5031ae` | `reports/UNCERTAIN_TERMINAL_STATUS.html` | `ba95ab00f881e197a235cb5d68c5aba0d7f74c8a` | 0 |
| `reports/WEDGE_DIAGNOSTICS_GATE.ru.html` | `1cab5f21faa14878a280de3bd32c1a85177b4ed3` | `reports/WEDGE_DIAGNOSTICS_GATE.html` | `3775d37e44b6571193b4813a28a2fc93d26c397c` | 0 |

## Results

- **57/57** original Russian-named report paths have an existing exact English HTML counterpart.
- **57/57** English report **contents actually fetched** at their recorded blob SHA; **50** have no literal Cyrillic, **seven** retain **383 total Cyrillic characters** in original-language owner statements, historic session names or exact approval tokens. Those are intended source/evidence exceptions, not generic prose eligible for blind translation.
- The pre-existing English reports remain intact. The separate [PM Bridge Draft PR #1](https://github.com/xLZDx/PM_Bridge/pull/1) contains two additional English Markdown explanatory reports, a new [57-report index](https://github.com/xLZDx/PM_Bridge/blob/docs/english-historical-reports-20261010/reports/ENGLISH_HISTORICAL_REPORTS_INDEX.md) and an English README link.
- At exact head `9cee55d933688abd0726566202090d48e01b04fc`, both navigation files were fetched and checked: **120 valid local Markdown links** across the new report index (119) and README (1), **zero missing destinations, zero Cyrillic**. Only **four Markdown files** are changed by the PR. No original HTML, code, policy marker or runtime configuration was changed.

## Two archived broken relative evidence references

`reports/GATE_P_LIVE_PROBES.html` includes two `href` references prefixed with `reports/`; since the HTML file itself is already in `reports/` and contains no HTML `<base>` element, they resolve to an absent `reports/reports/` path. The original English HTML report stays unchanged. The new [verified English index](https://github.com/xLZDx/PM_Bridge/blob/docs/english-historical-reports-20261010/reports/ENGLISH_HISTORICAL_REPORTS_INDEX.md) provides two correct adjacent-file links to `gate-p-h1-evidence.json` and `gate-p-h2-evidence.json` which are both tracked in Git.

## Existing active Markdown and operator-authorization exceptions

The prior [34-file PM Bridge Markdown/TXT classification](THREE_REPO_ACTIVE_TEXT_AUDIT_2026-10-10.md) found 21 with no Cyrillic and 13 source-bound exceptions in approval marker examples and verbatim owner language. Visually ambiguous Latin/Cyrillic gate references are a separate validation scope, and normalizing those tokens in place could break consumers or falsify historical semantics.

## Review boundaries

This is a **source-path, English-text presence and literal-language audit** of a fixed original-report cohort. It is not proof that historical deploy/test claims remain true, that the pages are semantically identical sentence by sentence, that every HTML anchor renders correctly, or that all code comments/feature branches/GitHub conversations are English.

**Known Russian-named report cohort:** 57/57 with existing English counterparts, **zero missing**. The two English Markdown explanatory reports are already in draft, and no new executable code, browser automation, database state, credentials or merge operation was performed.

**Disposition:** Historical report English coverage verified; independent semantic reviewer and authorized PR merge still pending; account-wide GitHub English migration **IN PROGRESS**.
